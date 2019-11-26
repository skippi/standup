"""Module for hosting shell-related functions."""

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
@click.argument("token", nargs=1, metavar="<token>")
def main(db_name: str, token: str):
    """Starts the standup bot."""

    DB.init(db_name)
    DB.connect()
    migrate(DB)

    BOT.run(token)
