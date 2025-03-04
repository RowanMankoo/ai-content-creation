import argparse
import logging

from reddit_post_processor import RedditPostProcessor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO: acctually make these effective options to pick when triggering cronjob
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch top Reddit posts with comments."
    )
    parser.add_argument("--subreddit", type=str, required=True, help="Subreddit name")
    parser.add_argument(
        "--n_posts", type=int, required=True, help="Number of posts to fetch"
    )
    parser.add_argument(
        "--n_comments", type=int, required=True, help="Number of comments per post"
    )
    parser.add_argument(
        "--time_filter",
        type=str,
        choices=["all", "year", "month", "week", "day", "hour"],
        required=True,
        help="Time filter for top posts",
    )
    parser.add_argument(
        "--gcp_bucket_video_source_blob_name",
        type=str,
        default="reddit_story_videos/source_videos/mc_parkour.mp4",
        help="GCP bucket blob name for the base video",
    )
    parser.add_argument(
        "--gcp_bucket_video_destination_blob_prefix",
        type=str,
        default="reddit_story_videos/processed_videos",
        help="GCP bucket blob prefix for the processed videos",
    )
    return parser.parse_args()


def run_job(
    subreddit,
    n_posts,
    n_comments,
    time_filter,
    gcp_bucket_name,
    gcp_bucket_video_source_blob_name,
    gcp_bucket_video_destination_blob_prefix,
):
    processor = RedditPostProcessor(
        subreddit=subreddit,
        n_posts=n_posts,
        n_comments=n_comments,
        time_filter=time_filter,
        gcp_bucket_name=gcp_bucket_name,
        gcp_bucket_video_source_blob_name=gcp_bucket_video_source_blob_name,
        gcp_bucket_video_destination_blob_prefix=gcp_bucket_video_destination_blob_prefix,
    )
    processor.create_videos()


if __name__ == "__main__":
    args = parse_arguments()
    run_job(
        subreddit=args.subreddit,
        n_posts=args.n_posts,
        n_comments=args.n_comments,
        time_filter=args.time_filter,
        gcp_bucket_name="ai-content-creation-438122-storage-bucket",
        gcp_bucket_video_source_blob_name=args.gcp_bucket_video_source_blob_name,
        gcp_bucket_video_destination_blob_prefix="reddit_story_videos/processed_videos",
    )
