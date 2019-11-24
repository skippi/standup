"""Module for persisting data."""

import pickle
from typing import Set

CHANNELS_FILE = "channels.pickle"


def load_channels() -> Set[int]:
    """Returns the set of channels that function as standup rooms."""

    with open(CHANNELS_FILE, "r+b") as file:
        try:
            return pickle.load(file)
        except EOFError:
            return set()


def save_channels(channels: Set[int]):
    """Updates the set of channels that function as standup rooms."""

    with open(CHANNELS_FILE, "wb") as file:
        pickle.dump(channels, file)
