"""Module for hosting shell-related functions."""

import os
import sys

import click
from standup.bot import BOT
from standup.persist import DB, migrate


@click.command(options_metavar="[options]")
@click.option(
    "-db",
    "--database",
    "db_name",
    nargs=1,
    help="sqlite database file",
    metavar="<database>",
    default="repo.db",
    show_default=True,
)
def main(db_name: str):
    """Starts the standup bot."""

    token = os.getenv("STANDUP_BOT_TOKEN")
    if not token:
        print(f"standup: invalid token `{token if token else ''}`")
        sys.exit(1)

    DB.init(db_name)
    DB.connect()
    migrate(DB)

    BOT.run(token)
