import os
import sys

from . import bot


def main():
    token = os.getenv("STANDUP_BOT_TOKEN")
    if not token:
        print(f"standup: invalid token `{token if token else ''}`")
        sys.exit(1)

    bot.BOT.run(token)
