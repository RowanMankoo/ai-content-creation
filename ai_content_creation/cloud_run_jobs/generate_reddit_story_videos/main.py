import argparse
import logging

from reddit_post_processor import RedditPostProcessor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
    return parser.parse_args()


def run_job(subreddit, n_posts, n_comments, time_filter):
    processor = RedditPostProcessor(
        subreddit=subreddit,
        n_posts=n_posts,
        n_comments=n_comments,
        time_filter=time_filter,
        base_video_path="/home/rowan/projects/ai-content-creation/mc_parkour.mp4",  # TODO: chnage
    )
    processor.create_videos()


if __name__ == "__main__":
    args = parse_arguments()
    run_job(args.subreddit, args.n_posts, args.n_comments, args.time_filter)
