"""Module for hosting shell-related functions."""

import os
import sys

from standup.bot import BOT
from standup.persist import DB, migrate


def main():
    """Entry point for `standup` script."""

    token = os.getenv("STANDUP_BOT_TOKEN")
    if not token:
        print(f"standup: invalid token `{token if token else ''}`")
        sys.exit(1)

    DB.init("repo.db")
    DB.connect()
    migrate(DB)

    BOT.run(token)
