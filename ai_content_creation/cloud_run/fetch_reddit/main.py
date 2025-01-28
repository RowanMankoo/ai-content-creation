from fastapi import FastAPI
import os
import praw
from data_models import (
    RedditPost,
    BatchRedditPost,
    RedditPostRequest,
    TimeFilter,
)
from logging import getLogger

CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
SECRET_KEY = os.environ.get("REDDIT_SECRET_KEY")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

app = FastAPI()
logger = getLogger(__name__) # TODO: get this working locally


def fetch_top_posts_with_comments_func(
    subreddit_name: str, n_posts: int, n_comments: int, time_filter: TimeFilter
):
    logger.info(
        f"Fetching top {n_posts} posts with top {n_comments} comments from {subreddit_name} subreddit."
    )
    reddit = praw.Reddit(
        client_id=CLIENT_ID, client_secret=SECRET_KEY, user_agent=USER_AGENT
    )

    subreddit = reddit.subreddit(subreddit_name)
    top_posts = subreddit.top(time_filter=time_filter, limit=n_posts)

    posts = []

    for post in top_posts:
        top_comments = []
        post.comments.replace_more(limit=0)  # Remove "More comments" links
        top_n_comments = post.comments.list()[:n_comments]

        for comment in top_n_comments:
            top_comments.append(comment.body)

        post_info = RedditPost(
            title=post.title,
            text=(
                post.selftext if post.selftext else "No self-text available."
            ),  # TODO: figure this out
            top_comments=top_comments,
        )

        posts.append(post_info)

    return BatchRedditPost(posts=posts)


@app.post("/fetch_reddit")
def fetch_top_posts_with_comments(
    reddit_post_request: RedditPostRequest,
) -> BatchRedditPost:
    logger.info("Fetching top posts with comments from Reddit.")

    res = fetch_top_posts_with_comments_func(
        reddit_post_request.subreddit_name,
        reddit_post_request.n_posts,
        reddit_post_request.n_comments,
        reddit_post_request.time_filter,
    )
    logger.info("Successfully fetched top posts with comments from Reddit.")
    return res


if __name__ == "__main__":
    app.run()
