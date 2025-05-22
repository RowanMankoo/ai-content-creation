import logging
from pathlib import Path

from openai import OpenAI

from src.gcp import GCPBucketHandler
from src.ffmpeg import combine_audio_video_images_subtitles
from src.reddit_title_card import make_reddit_card
from src.api_requests import (
    fetch_reddit_posts,
    create_audio_gcp,
    create_transcript,
    subtitle_to_video_metadata,
    create_cleaned_text_for_tts,
    cleaned_text_to_voice_gender_prediction,
    remove_title_from_ass_transcript,
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
        gcp_bucket_notification_sound_blob_name = (
            "reddit_story_videos/source_sounds/ding-126626.mp3"
        )
        # TODO: alter
        self.base_video_path = Path("/tmp/base_video.mp4")
        self.base_notification_sound_path = Path("/tmp/notification_sound.mp3")

        self.gcp_bucket_handler.download_file(
            gcp_bucket_video_source_blob_name, destination_file=self.base_video_path
        )
        self.gcp_bucket_handler.download_file(
            gcp_bucket_notification_sound_blob_name,
            destination_file=self.base_notification_sound_path,
        )

    def process_post(self, post, index):
        """Processes a single post: generates audio, transcribes, and overlays subtitles on a video."""
        output_dir = Path(f"/tmp/output_{index}")
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_file_path = output_dir / "audio.mp3"
        subtitle_file_path = output_dir / "transcript.ass"
        output_video_path = output_dir / "output.mp4"
        output_reddit_title_card_path = output_dir / "reddit_card.png"

        cleaned_text_dict = create_cleaned_text_for_tts(self.openai_client, post)

        make_reddit_card(
            title=cleaned_text_dict["cleaned_title"],
            username="Xcite9",  # TODO: credit acc author
            subreddit="xcite9",  # TODO: put acc subreddit
            output=output_reddit_title_card_path,
        )

        male = cleaned_text_to_voice_gender_prediction(
            self.openai_client, cleaned_text_dict["cleaned_combined_text"]
        )
        create_audio_gcp(
            cleaned_text_dict["cleaned_combined_text"],
            male,
            audio_file_path,
        )
        transcript = create_transcript(self.openai_client, audio_file_path)
        images, video_description, video_tags = subtitle_to_video_metadata(
            self.openai_client, transcript
        )
        _, reddit_title_card_start_ts, reddit_title_card_end_ts = (
            remove_title_from_ass_transcript(
                openai_client=self.openai_client,
                transcript=transcript,
                title_to_remove=cleaned_text_dict["cleaned_title"],
                subtitle_file_path=subtitle_file_path,
            )
        )

        combine_audio_video_images_subtitles(
            audio_file_path=audio_file_path,
            video_file_path=self.base_video_path,
            notification_sound_path=self.base_notification_sound_path,
            subtitle_file_path=subtitle_file_path,
            image_timeline=images,
            reddit_card_path=output_reddit_title_card_path,
            reddit_title_card_start_ts=reddit_title_card_start_ts,
            reddit_title_card_end_ts=reddit_title_card_end_ts,
            output_file_path=output_video_path,
            vertical_offset_pct=0.1,
        )

        logger.info(f"Post {index} processed.")

        self.gcp_bucket_handler.upload_processsed_video(
            local_processed_video_path=output_video_path,
            video_number=index,
            video_description=video_description,
            video_tags=video_tags,
        )
        logger.info(f"Uploaded processed video {output_video_path} to GCP bucket.")

    # TODO: custom eror handling for out of credits
    def process_all_posts(self, reddit_posts: dict):
        """Processes all fetched Reddit posts."""

        success_count = 0
        for i, post in enumerate(reddit_posts):
            if success_count >= self.n_posts:
                logger.info("Reached required number of posts.")
                break
            logger.info(f"Processing post {i}...")
            try:
                self.process_post(post, i)
                success_count += 1
            except Exception as e:
                logger.error(f"Error processing post {i}: {e}")

        if success_count < self.n_posts:
            logger.warning(f"Only made {success_count}/{self.n_posts} videos")

    def create_videos(self):
        """Runs the complete processing pipeline."""
        reddit_posts = fetch_reddit_posts(
            n_posts=self.n_posts * 2,  # fetch double the posts to account for errors
            n_comments=self.n_comments,
            subreddit=self.subreddit,
            time_filter=self.time_filter,
        )
        self.process_all_posts(reddit_posts)
        logger.info("All posts processed.")
