"""Module for persisting data."""

import pickle
from dataclasses import dataclass
from datetime import datetime
from typing import List, Set


CHANNELS_FILE = "channels.pickle"
POSTS_FILE = "posts.pickle"


@dataclass
class Post:
    """
    Represents an active standup post.

    Posts are active if their age is less than 24 hours.
    """

    channel_id: int
    user_id: int
    roles: Set[int]
    timestamp: datetime


def load_posts() -> List[Post]:
    """Returns the list of active posts."""

    try:
        with open(POSTS_FILE, "r+b") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []
    except EOFError:
        return []


def save_posts(posts: List[Post]):
    """Updates the list of active posts."""

    with open(POSTS_FILE, "wb") as file:
        pickle.dump(posts, file)


def load_channels() -> Set[int]:
    """Returns the set of channels that function as standup rooms."""

    try:
        with open(CHANNELS_FILE, "r+b") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return set()
    except EOFError:
        return set()


def save_channels(channels: Set[int]):
    """Updates the set of channels that function as standup rooms."""

    with open(CHANNELS_FILE, "wb") as file:
        pickle.dump(channels, file)
