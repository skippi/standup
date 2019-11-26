"""Module for interacting with standup posts."""

import re


STANDUP_REGEX = (
    r"^Yesterday I:[\s\S]+\n"
    r"Today I will:[\s\S]+\n"
    r"Potential hard problems:[\s\S]+$"
)


def message_is_formatted(msg: str):
    """Return `True` if `msg` matches the standup format."""

    return re.match(STANDUP_REGEX, msg)
