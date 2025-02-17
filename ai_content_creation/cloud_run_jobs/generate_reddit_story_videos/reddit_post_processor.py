import logging
import os
from pathlib import Path

import praw
from openai import OpenAI
from subtitle_formatting import convert_srt_to_ass
from google.cloud import storage


logger = logging.getLogger(__name__)

CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
SECRET_KEY = os.environ.get("REDDIT_SECRET_KEY")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT")


# TODO: define Post pydantic class and pass it around to diff funcs
# TODO: improve error handling
# TODO: deal with video being shorter than audio
# TODO: add sound
# TODO: don't process reddit story if it is longer than threshold, 4096 characters is limit
# TODO: allow for differnt videos
# TODO: set up videos in bucket and allow access
class RedditPostProcessor:
    """Handles fetching, processing, and combining Reddit posts into videos."""

    def __init__(self, subreddit, n_posts, n_comments, time_filter, base_video_path):
        self.subreddit = subreddit
        self.n_posts = n_posts
        self.n_comments = n_comments
        self.time_filter = time_filter
        self.base_video_path = base_video_path
        self.openai_client = OpenAI()
        self.reddit_posts = []

        RedditPostProcessor.download_blob()

    # TODO: clean up
    @staticmethod
    def download_blob(
        bucket_name="ai-content-creation-438122-storage-bucket",
        source_blob_name="reddit_story_videos/source_videos/mc_parkour.mp4",
        destination_file_name="/tmp/mc_parkour.mp4",
    ):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Downloaded {source_blob_name} to {destination_file_name}")

    def fetch_posts(self):

        logger.info(
            f"Fetching top {self.n_posts} posts with top {self.n_comments} comments from {self.subreddit} subreddit."
        )

        reddit = praw.Reddit(
            client_id=CLIENT_ID, client_secret=SECRET_KEY, user_agent=USER_AGENT
        )
        subreddit = reddit.subreddit(self.subreddit)
        top_posts = subreddit.top(time_filter=self.time_filter, limit=self.n_posts)

        self.reddit_posts = []
        for post in top_posts:
            top_comments = []
            post.comments.replace_more(limit=0)  # Remove "More comments" links
            top_n_comments = post.comments.list()[: self.n_comments]

            for comment in top_n_comments:
                top_comments.append(comment.body)

            post_info = {
                "title": post.title,
                "text": post.selftext if post.selftext else "No self-text available.",
                "top_comments": top_comments,
            }

            self.reddit_posts.append(post_info)

    def create_audio(self, post: dict, audio_file_path: Path):

        audio_response = self.openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=post["title"] + "\n" + post["text"],
        )
        audio_response.stream_to_file(audio_file_path)

    def create_transcript(self, audio_file_path: Path, subtitle_file_path: Path):

        with open(audio_file_path, "rb") as audio_file:
            srt_transcript = self.openai_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="srt",
            )
        ass_transcript = convert_srt_to_ass(srt_transcript)
        subtitle_file_path.write_text(ass_transcript)

    def combine_audio_video_subtitles(
        self,
        audio_file_path: Path,
        video_file_path: Path,
        subtitle_file_path: Path,
        output_file_path: Path,
    ):
        os.system(
            f"ffmpeg -i {video_file_path} -i {audio_file_path} -vf subtitles={subtitle_file_path} "
            f"-map 0:v -map 1:a -shortest {output_file_path}"
        )

    def process_post(self, post, index):
        """Processes a single post: generates audio, transcribes, and overlays subtitles on a video."""
        output_dir = Path(f"/tmp/output_{index}")
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_file_path = output_dir / "audio.mp3"
        subtitle_file_path = output_dir / "transcript.srt"
        output_video_path = output_dir / "output.mp4"

        self.create_audio(post, audio_file_path)
        self.create_transcript(audio_file_path, subtitle_file_path)
        self.combine_audio_video_subtitles(
            audio_file_path, self.base_video_path, subtitle_file_path, output_video_path
        )

        logger.info(f"Post {index} processed.")

    def process_all_posts(self):
        """Processes all fetched Reddit posts."""
        if not self.reddit_posts:
            logger.warning("No posts fetched. Run fetch_posts() first.")
            return

        for i, post in enumerate(self.reddit_posts):
            logger.info(f"Processing post {i}...")
            try:
                self.process_post(post, i)
            except Exception as e:
                logger.error(f"Error processing post {i}: {e}")


    def create_videos(self):
        """Runs the complete processing pipeline."""
        self.fetch_posts()
        self.process_all_posts()
