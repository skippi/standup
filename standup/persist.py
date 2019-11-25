"""Module for persisting data."""

import pickle
from datetime import datetime
from typing import Dict, Set

CHANNELS_FILE = "channels.pickle"
DATES_FILE = "dates.pickle"


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


def load_previous_standup_date_from_user(user_id: int) -> datetime:
    """Returns the previous time a user posted for a standup."""

    user_dates = _load_user_standup_dates()
    return user_dates.get(user_id)


def update_standup_date_for_user(user_id: int, date: datetime):
    """Updates the previous time a user posted for a standup."""

    user_dates = _load_user_standup_dates()
    user_dates[user_id] = date
    _save_user_standup_dates(user_dates)


def _load_user_standup_dates() -> Dict[int, datetime]:
    try:
        with open(DATES_FILE, "r+b") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}
    except EOFError:
        return {}


def _save_user_standup_dates(user_dates: Dict[int, datetime]):
    with open(DATES_FILE, "wb") as file:
        pickle.dump(user_dates, file)
