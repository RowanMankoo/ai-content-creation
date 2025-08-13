import logging
import os
import requests
import json

import praw
from openai import OpenAI
from pathlib import Path
from google.cloud import texttospeech
from google.cloud import speech

from src.subtitle_formatting import (
    make_ass_from_words,
    make_ass_from_google_response,
)
from deepgram import DeepgramClient, PrerecordedOptions
from src.prompts import (
    TITLE_CLEANING_PROMPT,
    TEXT_CLEANING_PROMPT,
    SUBTITLE_TO_VIDEO_METADATA_PROMPT,
    DEFAULT_TAGS,
    CLEANED_TEXT_TO_VOICE_GENDER_PREDICTION_PROMPT,
    TITLE_DETECTION_PROMPT,
    IMAGE_STYLE_PROMPT,
)

# TODO: move this to config
MALE_VOICE_MAPPER = {
    0: "en-US-Chirp3-HD-Achernar",
    1: "en-US-Chirp3-HD-Achird",
}

logger = logging.getLogger(__name__)


def fetch_reddit_posts(n_posts, n_comments, subreddit_name, time_filter) -> list:
    logger.info(
        f"Fetching top {n_posts} posts with top {n_comments} comments from '{subreddit_name}' subreddit."
    )

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_SECRET_KEY"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
    )
    subreddit = reddit.subreddit(subreddit_name)
    top_posts = subreddit.top(time_filter=time_filter, limit=n_posts)

    results = []
    for post in top_posts:
        post.comments.replace_more(limit=0)
        comments = []
        for comment in post.comments.list()[:n_comments]:
            comments.append(
                {
                    "username": comment.author.name if comment.author else "[deleted]",
                    "body": comment.body,
                }
            )

        results.append(
            {
                "title": post.title,
                "post_username": (post.author.name if post.author else "[deleted]"),
                "subreddit": subreddit_name,
                "text": post.selftext or "No self-text available.",
                "top_comments": comments,
            }
        )

    return results


def runware_image_generation(
    image_description: str,
    resolution: str = "640x1152",
) -> str:
    """
    Generates images based on the provided descriptions using Runware API. Returns the URL of the generated image.
    """
    w, h = map(int, resolution.split("x"))
    h_half = h // 2

    url = "https://api.runware.ai/v1"
    key = os.environ["RUNWARE_API_KEY"]
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = [
        {
            "taskType": "imageInference",
            "taskUUID": "7ef68268-fd5c-4c92-81e8-069b16d4eaab",
            "width": w,
            "height": h_half,
            "numberResults": 1,
            "outputFormat": "JPEG",
            "steps": 30,
            "CFGScale": 3,
            "scheduler": "UniPCMultistepScheduler",
            "outputType": ["URL"],
            "includeCost": True,
            "positivePrompt": image_description,
            "model": "runware:108@1",
        }
    ]

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["data"][0]["imageURL"]


def create_audio_gcp(
    text: str,
    male: bool,
    audio_file_path: Path,
    speaking_rate: float = 1.1,
):
    # Enforce a 5k character limit to avoid oversized TTS requests
    if len(text) > 5000:
        logger.warning(
            f"Text length ({len(text)}) exceeds 5000 characters, skipping TTS."
        )
        return

    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name=MALE_VOICE_MAPPER[male]
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate,
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(audio_file_path, "wb") as out:
        out.write(response.audio_content)

    logger.info(f"Created and saved audio to {audio_file_path}")


def create_transcript(
    openai_client: OpenAI,
    audio_file_path: Path,
) -> str:

    with open(audio_file_path, "rb") as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            language="en",
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    ass_transcript = make_ass_from_words(transcript.words)
    logger.info(f"Created ASS Subtitle Transcript: {ass_transcript}")

    return ass_transcript


def create_transcript_gcs(gcs_uri: str) -> str:
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=24000,
        language_code="en-US",
        enable_word_time_offsets=True,
    )
    response = client.recognize(config=config, audio=audio)
    return make_ass_from_google_response(response)

def create_transcript_deepgram(audio_file_path: Path) -> str:
    key = os.environ["DEEPGRAM_API_KEY"]
    deepgram_client = DeepgramClient(key)

    with open(audio_file_path, "rb") as audio_file:
        source: dict = {"stream": audio_file}
        options = PrerecordedOptions(model="nova-3")
        response = deepgram_client.listen.rest.v("1").transcribe_file(
            source=source,
            options=options,
        )
        words = response.results.channels[0].alternatives[0].words
    return make_ass_from_words(words)

def create_cleaned_text_for_tts(openai_client: OpenAI, post: dict) -> dict[str]:
    title_response = openai_client.chat.completions.create(
        model="gpt-4.1",  # not mini here as tends to hallucinate rest of story for some reason
        messages=[
            {"role": "system", "content": TITLE_CLEANING_PROMPT},
            {"role": "user", "content": post["title"]},
        ],
        temperature=0,
    )
    text_response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": TEXT_CLEANING_PROMPT},
            {"role": "user", "content": post["text"]},
        ],
        temperature=0,
    )

    cleaned_title = title_response.choices[0].message.content
    cleaned_text = text_response.choices[0].message.content

    logger.info(f"Cleaned text for TTS: cleaned_title: {cleaned_title}")
    logger.info(f"Cleaned text for TTS: cleaned_text: {cleaned_text}")

    return {
        "cleaned_title": cleaned_title,
        "cleaned_text": cleaned_text,
        "cleaned_combined_text": cleaned_title + "\n\n" + cleaned_text,
    }


# TODO: split this func out
def subtitle_to_video_metadata(
    openai_client: OpenAI, transcript: str, reddit_title_card_end_ts: str
) -> tuple[list[dict], str, list[str]]:

    response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SUBTITLE_TO_VIDEO_METADATA_PROMPT},
            {
                "role": "user",
                "content": transcript.split("[Events]")[-1]
                + f"\nFirst image end time: {reddit_title_card_end_ts}",
            },
        ],
        temperature=0.5,
    )
    raw_response = response.choices[0].message.content
    logger.info(f"Raw response from OpenAI: {raw_response}")
    json_response = json.loads(raw_response)

    images = json_response["images"]
    video_description = json_response["video_description"]
    video_tags = json.loads(DEFAULT_TAGS) + json_response["video_tags"]

    for image in images:
        image["image_url"] = runware_image_generation(
            image_description=image["description"] + " " + IMAGE_STYLE_PROMPT
        )
    return images, video_description, video_tags


def cleaned_text_to_voice_gender_prediction(
    openai_client: OpenAI, transcript: str
) -> bool:

    response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": CLEANED_TEXT_TO_VOICE_GENDER_PREDICTION_PROMPT,
            },
            {"role": "user", "content": transcript.split("[Events]")[-1]},
        ],
        temperature=0.5,
    )
    raw_response = response.choices[0].message.content
    logger.info(f"Raw response from OpenAI: {raw_response}")
    json_response = json.loads(raw_response)

    male = json_response["male"]

    return male


def remove_title_from_ass_transcript(
    openai_client: OpenAI,
    transcript: str,
    title_to_remove: str,
    subtitle_file_path: Path,
    n_lines: int = 100,
) -> tuple[str]:

    logger.info("Starting title removal from transcript.")
    events_start_phrase = "[Events]\n"
    split_transcript = transcript.split(events_start_phrase)
    transcript_info_and_styles, transcript_subtitle_text_and_timings = (
        split_transcript[0],
        split_transcript[-1],
    )

    transcript_subtitle_text_and_timings_list = (
        transcript_subtitle_text_and_timings.split("\n")
    )

    # only send n_lines in to avoid using too many tokens
    lines = json.dumps(transcript_subtitle_text_and_timings_list[:n_lines])
    logger.debug(f"Extracted first {n_lines} lines for processing: {lines}")

    resp = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": TITLE_DETECTION_PROMPT.strip()},
            {"role": "user", "content": f"Title: {title_to_remove}\nLines:\n{lines}"},
        ],
        temperature=0,
    )

    raw = resp.choices[0].message.content
    logger.info(f"Raw response from OpenAI: {raw}")

    start_line, end_line, start_ts, end_ts = json.loads(raw)

    title_removed_transcript_subtitle_text_and_timings_list = (
        transcript_subtitle_text_and_timings_list[:start_line]
        + transcript_subtitle_text_and_timings_list[end_line + 1 :]
    )
    title_removed_transcript = (
        transcript_info_and_styles
        + events_start_phrase
        + "\n".join(title_removed_transcript_subtitle_text_and_timings_list)
    )

    subtitle_file_path.write_text(title_removed_transcript)
    logger.info(
        f"Title successfully removed from transcript and saved to file: {subtitle_file_path}"
    )

    return title_removed_transcript, start_ts, end_ts
