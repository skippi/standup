"""Module for persisting data."""

import pickle
from dataclasses import dataclass
from datetime import datetime
from typing import List, Set


ROOMS_FILE = "rooms.pickle"
POSTS_FILE = "posts.pickle"


@dataclass
class Post:
    """
    Represents an active standup post.

    Posts are active if their age is less than 24 hours.
    """

    channel_id: int
    user_id: int
    role_ids: Set[int]
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


@dataclass
class Room:
    """
    Represents a standup channel.
    """

    channel_id: int
    role_ids: Set[int]


def load_rooms() -> List[Room]:
    """Returns the list of active rooms."""

    try:
        with open(ROOMS_FILE, "r+b") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []
    except EOFError:
        return []


def save_rooms(rooms: List[int]):
    """Updates the list of active rooms."""

    with open(ROOMS_FILE, "wb") as file:
        pickle.dump(rooms, file)
