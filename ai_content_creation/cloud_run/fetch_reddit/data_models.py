from pydantic import BaseModel, Field
from enum import Enum


class RedditPost(BaseModel):
    title: str
    text: str
    top_comments: list[str]


class BatchRedditPost(BaseModel):
    posts: list[RedditPost]


class TimeFilter(str, Enum):
    all = "all"
    year = "year"
    month = "month"
    week = "week"
    day = "day"
    hour = "hour"


class RedditPostRequest(BaseModel):
    subreddit_name: str = Field(..., example="AmItheAsshole")
    n_posts: int = Field(..., example=5)
    n_comments: int = Field(..., example=3)
    time_filter: TimeFilter = Field(..., example="day")
