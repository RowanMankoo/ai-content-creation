import argparse
import logging

from src.reddit_post_processor import RedditPostProcessor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch top Reddit posts with comments."
    )
    parser.add_argument(
        "--subreddit", type=str, default="AmITheAsshole", help="Subreddit name"
    )
    parser.add_argument(
        "--n_posts", type=int, default=1, help="Number of posts to fetch"
    )
    parser.add_argument(
        "--n_comments", type=int, default=1, help="Number of comments per post"
    )
    parser.add_argument(
        "--time_filter",
        type=str,
        choices=["all", "year", "month", "week", "day", "hour"],
        default="day",
        help="Time filter for top posts",
    )
    parser.add_argument(
        "--gcp_bucket_video_destination_blob_prefix",
        type=str,
        default="reddit_story_videos/processed_videos",
        help="GCP bucket blob prefix for the processed videos",
    )
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_arguments()

    processor = RedditPostProcessor(
        subreddit=args.subreddit,
        n_posts=args.n_posts,
        n_comments=args.n_comments,
        time_filter=args.time_filter,
        gcp_bucket_name="ai-content-creation-438122-storage-bucket",
        gcp_bucket_video_destination_blob_prefix="reddit_story_videos/processed_videos",
    )
    processor.create_videos()
