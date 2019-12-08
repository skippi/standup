"""Module for hosting shell-related functions."""

import os
from pathlib import Path

import click
from standup.bot import BOT
from standup.persist import DB, initialize


@click.command(options_metavar="[options]")
@click.option(
    "-db",
    "--database",
    "db_path",
    nargs=1,
    help="sqlite database file",
    metavar="<database>",
    default="repo.db",
    show_default=True,
)
@click.argument("token", nargs=1, metavar="<token>")
def main(db_path: str, token: str) -> None:
    """Starts the standup bot."""

    db_path_dir = Path(db_path).parents[0]
    os.makedirs(db_path_dir, exist_ok=True)
    DB.init(db_path)
    DB.connect()
    initialize(DB)

    BOT.run(token)
