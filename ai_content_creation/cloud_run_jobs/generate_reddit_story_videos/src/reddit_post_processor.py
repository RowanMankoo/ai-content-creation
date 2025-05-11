import logging
from pathlib import Path

from openai import OpenAI

from src.gcp import GCPBucketHandler
from src.ffmpeg import combine_audio_video_images_subtitles
from src.api_requests import (
    fetch_reddit_posts,
    create_audio,
    create_transcript,
    subtitle_to_video_metadata,
    create_cleaned_text_for_tts,
    cleaned_text_to_voice_description_metadata
)

logger = logging.getLogger(__name__)


class RedditPostProcessor:
    """Handles fetching, processing, and combining Reddit posts into videos."""

    def __init__(
        self,
        subreddit,
        n_posts,
        n_comments,
        time_filter,
        gcp_bucket_name: str,
        gcp_bucket_video_destination_blob_prefix: str,
    ):
        self.subreddit = subreddit
        self.n_posts = n_posts
        self.n_comments = n_comments
        self.time_filter = time_filter
        self.openai_client = OpenAI()
        self.reddit_posts = []

        self.gcp_bucket_handler = GCPBucketHandler(
            bucket_name=gcp_bucket_name,
            gcp_bucket_video_destination_blob_prefix=gcp_bucket_video_destination_blob_prefix,
        )
        gcp_bucket_video_source_blob_name = (
            "reddit_story_videos/source_videos/mc_parkour.mp4"
            # "reddit_story_videos/source_videos/RPReplay_Final1746657961.mp4"
        )
        # TODO: alter
        self.base_video_path = Path("/tmp/base_video.mp4")
        self.gcp_bucket_handler.download_file(
            gcp_bucket_video_source_blob_name, destination_file=self.base_video_path
        )

    def process_post(self, post, index):
        """Processes a single post: generates audio, transcribes, and overlays subtitles on a video."""
        output_dir = Path(f"/tmp/output_{index}")
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_file_path = output_dir / "audio.mp3"
        subtitle_file_path = output_dir / "transcript.ass"
        output_video_path = output_dir / "output.mp4"

        cleaned_text = create_cleaned_text_for_tts(self.openai_client, post)
        male, voice_instructions = cleaned_text_to_voice_description_metadata(
            self.openai_client, cleaned_text
        )
        create_audio(self.openai_client, cleaned_text, male, voice_instructions, audio_file_path)
        transcript = create_transcript(
            self.openai_client, audio_file_path, subtitle_file_path
        )
        images, video_description, video_tags = subtitle_to_video_metadata(
            self.openai_client, transcript
        )

        combine_audio_video_images_subtitles(
            audio_file_path=audio_file_path,
            video_file_path=self.base_video_path,
            subtitle_file_path=subtitle_file_path,
            image_timeline=images,
            output_file_path=output_video_path,
            vertical_offset_pct=0.1,  # TODO: put this as configmap somewhere
        )

        logger.info(f"Post {index} processed.")

        self.gcp_bucket_handler.upload_processsed_video(
            local_processed_video_path=output_video_path,
            video_number=index,
            video_description=video_description,
            video_tags=video_tags,
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
        self.reddit_posts = fetch_reddit_posts(
            n_posts=self.n_posts,
            n_comments=self.n_comments,
            subreddit=self.subreddit,
            time_filter=self.time_filter,
        )
        self.process_all_posts()
