import logging
import os
import requests
import json

import praw
from openai import OpenAI
from pathlib import Path

from src.subtitle_formatting import convert_srt_to_ass
from src.prompts import (
    TEXT_CLEANING_PROMPT,
    SUBTITLE_TO_VIDEO_METADATA_PROMPT,
    CLEANED_TEXT_TO_VOICE_DESCRIPTION_PROMPT,
    TITLE_DETECTION_PROMPT,
    IMAGE_STYLE_PROMPT,
)

# TODO: move this to config
MALE_VOICE_MAPPER = {
    0: "nova",
    1: "ash",
}

logger = logging.getLogger(__name__)


# TODO: async
def fetch_reddit_posts(n_posts, n_comments, subreddit, time_filter) -> list:

    logger.info(
        f"Fetching top {n_posts} posts with top {n_comments} comments from {subreddit} subreddit."
    )

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_SECRET_KEY"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
    )
    subreddit = reddit.subreddit(subreddit)
    top_posts = subreddit.top(time_filter=time_filter, limit=n_posts)

    reddit_posts = []
    for post in top_posts:
        top_comments = []
        post.comments.replace_more(limit=0)  # Remove "More comments" links
        top_n_comments = post.comments.list()[:n_comments]

        for comment in top_n_comments:
            top_comments.append(comment.body)

        post_info = {
            "title": post.title,
            "text": post.selftext if post.selftext else "No self-text available.",
            "top_comments": top_comments,
        }

        reddit_posts.append(post_info)
    return reddit_posts


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
            "taskUUID": "97f88698-f178-4eb9-827b-f6eda9dda1d0",
            "width": w,
            "height": h_half,
            "numberResults": 1,
            "outputFormat": "JPEG",
            "steps": 33,
            "CFGScale": 3,
            "scheduler": "Euler Beta",
            "outputType": ["URL"],
            "includeCost": True,
            "seed": 1258323831228332,
            "positivePrompt": image_description,
            "model": "rundiffusion:130@100",
            "lora": [{"model": "civitai:829769@928048", "weight": 1}],
        }
    ]

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["data"][0]["imageURL"]


def create_audio(
    openai_client: OpenAI,
    text: str,
    male: bool,
    voice_instructions: str,
    audio_file_path: Path,
):

    with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=MALE_VOICE_MAPPER[male],
        input=text,
        instructions=voice_instructions,
    ) as response:
        response.stream_to_file(audio_file_path)

    logger.info(f"Created and saved audio to {audio_file_path}")


def create_transcript(
    openai_client: OpenAI,
    audio_file_path: Path,
) -> str:

    with open(audio_file_path, "rb") as audio_file:
        srt_transcript = openai_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="srt",
        )
    ass_transcript = convert_srt_to_ass(srt_transcript)
    logger.info(f"Created ASS Subtitle Transcript: {ass_transcript}")

    return ass_transcript


def create_cleaned_text_for_tts(openai_client: OpenAI, post: dict) -> dict[str]:
    title_response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": TEXT_CLEANING_PROMPT},
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
def subtitle_to_video_metadata(openai_client: OpenAI, transcript: str) -> list[dict]:

    response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SUBTITLE_TO_VIDEO_METADATA_PROMPT},
            {"role": "user", "content": transcript.split("[Events]")[-1]},
        ],
        temperature=0.5,
    )
    raw_response = response.choices[0].message.content
    logger.info(f"Raw response from OpenAI: {raw_response}")
    json_response = json.loads(raw_response)

    images = json_response["images"]
    video_description = json_response["video_description"]
    video_tags = json_response["video_tags"]

    for image in images:
        image["image_url"] = runware_image_generation(
            image_description=image["description"] + " " + IMAGE_STYLE_PROMPT
        )
    return images, video_description, video_tags


def cleaned_text_to_voice_description_metadata(
    openai_client: OpenAI, transcript: str
) -> list[dict]:

    response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": CLEANED_TEXT_TO_VOICE_DESCRIPTION_PROMPT},
            {"role": "user", "content": transcript.split("[Events]")[-1]},
        ],
        temperature=0.5,
    )
    raw_response = response.choices[0].message.content
    logger.info(f"Raw response from OpenAI: {raw_response}")
    json_response = json.loads(raw_response)

    male = json_response["male"]
    voice_instructions = json_response["voice_instructions"]

    return male, voice_instructions


def remove_title_from_ass_transcript(
    openai_client: OpenAI,
    transcript: str,
    title_to_remove: str,
    subtitle_file_path: Path,
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

    # only send 15 lines in to avoid using too many tokens
    lines = json.dumps(transcript_subtitle_text_and_timings_list[:15])
    logger.debug(f"Extracted first 15 lines for processing: {lines}")

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
