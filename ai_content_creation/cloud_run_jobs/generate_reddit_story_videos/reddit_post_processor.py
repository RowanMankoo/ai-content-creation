import logging
import os
from pathlib import Path

import praw
from openai import OpenAI
from subtitle_formatting import convert_srt_to_ass
from google.cloud import storage
from pydantic_settings import BaseSettings
from datetime import datetime
import subprocess


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


class GCPBucketHandler:
    def __init__(self, bucket_name: str):
        """Initialize the GCP bucket handler."""
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()

    def download_file(self, source_blob_name: str, destination_file: str) -> Path:
        """
        Download a file from a GCP bucket.

        Args:
            source_blob_name (str): The path of the file in the GCP bucket.
            destination_folder (str): The local folder to save the file.

        Returns:
            Path: The local file path where the file was downloaded.
        """
        logger.info(
            f"Downloading {source_blob_name} from bucket {self.bucket_name} to {destination_file}"
        )

        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(str(destination_file))

        logger.info(f"Downloaded {source_blob_name} to {destination_file}")
        return destination_file

    def upload_file(self, source_file: str, destination_blob_name: str):
        """
        Upload a file to a GCP bucket.

        Args:
            source_file (str): The local file path to upload.
            destination_blob_name (str): The destination path in the GCP bucket.
        """
        source_file_path = Path(source_file)
        if not source_file_path.exists():
            raise FileNotFoundError(f"Source file {source_file} not found.")

        logger.info(
            f"Uploading {source_file} to {destination_blob_name} in bucket {self.bucket_name}"
        )

        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(str(source_file_path))

        logger.info(f"File {source_file} uploaded to {destination_blob_name}.")


class RedditPostProcessor:
    """Handles fetching, processing, and combining Reddit posts into videos."""

    def __init__(
        self,
        subreddit,
        n_posts,
        n_comments,
        time_filter,
        gcp_bucket_name: str,
        gcp_bucket_video_source_blob_name: str,
        gcp_bucket_video_destination_blob_prefix: str,
    ):
        self.subreddit = subreddit
        self.n_posts = n_posts
        self.n_comments = n_comments
        self.time_filter = time_filter
        self.openai_client = OpenAI()
        self.reddit_posts = []

        self.gcp_bucket_handler = GCPBucketHandler(bucket_name=gcp_bucket_name)
        self.gcp_bucket_video_destination_blob_prefix = (
            gcp_bucket_video_destination_blob_prefix
        )

        self.base_video_path = "/tmp/base_video.mp4"
        self.gcp_bucket_handler.download_file(
            gcp_bucket_video_source_blob_name, destination_file=self.base_video_path
        )

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

        logger.info(f"Created and saved audio to {audio_file_path}")

    def create_transcript(self, audio_file_path: Path, subtitle_file_path: Path):

        with open(audio_file_path, "rb") as audio_file:
            srt_transcript = self.openai_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="srt",
            )
        ass_transcript = convert_srt_to_ass(srt_transcript)
        subtitle_file_path.write_text(ass_transcript)

        logger.info(f"Created and saved transcript to {subtitle_file_path}")

    def combine_audio_video_subtitles(
        self,
        audio_file_path: Path,
        video_file_path: Path,
        subtitle_file_path: Path,
        output_file_path: Path,
    ):
        """Combines audio, video, and subtitles using FFmpeg with better error handling."""

        # Ensure all input files exist
        for file_path in [audio_file_path, video_file_path, subtitle_file_path]:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file {file_path} does not exist.")

        # FFmpeg command as a list (safe from shell injection)
        command = [
            "ffmpeg",
            "-i",
            str(video_file_path),  # Input video
            "-i",
            str(audio_file_path),  # Input audio
            "-vf",
            f"subtitles={subtitle_file_path}",  # Add subtitles
            "-map",
            "0:v",
            "-map",
            "1:a",  # Map video from input 0, audio from input 1
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-strict",
            "experimental",  # Encoding options
            "-shortest",  # Stop at the shortest input length
            "-y",
            str(output_file_path),  # Overwrite output file if exists
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,  # Raises error if FFmpeg fails
            )

            logger.info(f"FFmpeg Output: {result.stdout}")
            logger.info(f"Created and saved processed video to {output_file_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed with error: {e.stderr}")
            raise RuntimeError(f"FFmpeg process failed: {e.stderr}")

    def upload_processsed_video(
        self, local_processed_video_path: str, video_number: int
    ):
        today = datetime.now().strftime("%Y_%m_%d")
        timestamp = datetime.now().strftime("%H%M%S")

        destination_blob_name = str(
            Path(self.gcp_bucket_video_destination_blob_prefix)
            / Path(f"{today}/output_{str(video_number)}_{timestamp}.mp4")
        )
        self.gcp_bucket_handler.upload_file(
            local_processed_video_path, destination_blob_name
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

        self.upload_processsed_video(
            local_processed_video_path=output_video_path, video_number=index
        )
        logger.info(f"Uploaded processed video {output_video_path} to GCP bucket.")

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
