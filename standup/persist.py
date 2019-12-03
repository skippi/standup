"""Module for persisting data."""

from datetime import datetime, timezone
from typing import Any

from peewee import CharField, DateTimeField, Model, SqliteDatabase, Field, IntegerField


DB = SqliteDatabase("repo.db")


class _SnowflakeField(CharField):
    def db_value(self, value: Any) -> Any:
        if isinstance(value, int):
            return str(value)

        return super().db_value(value)

    def python_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return int(value)

        return super().python_value(value)


class _RoleSetField(Field):
    def db_value(self, value: Any) -> Any:
        if isinstance(value, set):
            return ",".join(str(i) for i in value)

        return super().db_value(value)

    def python_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return set(int(s) for s in value.split(",") if s)

        return super().python_value(value)


class _BaseModel(Model):
    # pylint: disable=missing-class-docstring,too-few-public-methods
    class Meta:
        database = DB


class Post(_BaseModel):
    """
    Represents an active standup post.

    Posts are active if their age is less than 24 hours.
    """

    channel_id = _SnowflakeField()
    user_id = _SnowflakeField()
    role_ids = _RoleSetField()
    timestamp = DateTimeField()

    @classmethod
    def create(cls, **query):
        if "timestamp" in query:
            assert query["timestamp"].tzinfo == timezone.utc
            query["timestamp"] = query["timestamp"].replace(
                tzinfo=None
            )  # peewee only likes naive datetimes

        return super().create(**query)

    @classmethod
    def select_expired_posts(cls, utc_time: datetime):
        """Selects expired posts according to `utc_time`."""

        assert utc_time.tzinfo == timezone.utc

        return (
            Post.select()
            .join(Room, on=(Post.channel_id == Room.channel_id))
            .where(
                (Post.timestamp.to_timestamp() + Room.cooldown)
                < int(utc_time.timestamp())
            )
        )


class Room(_BaseModel):
    """
    Represents a standup channel.

    Attributes:
        channel_id (integer): Room channel id.
        role_ids (Set[integer]): Room role ids to assign.
        cooldown (integer): Cooldown per stand-up post in seconds.
    """

    channel_id = _SnowflakeField()
    role_ids = _RoleSetField()
    cooldown = IntegerField(default=86400)

    def format_for_listing(self) -> str:
        """Formats the Room for the `rooms list` command."""

        roles_str = str(self.role_ids) if self.role_ids else "{}"
        return f"{self.channel_id} | Cooldown: {self.cooldown} | Roles: {roles_str}"


def migrate(database: SqliteDatabase):
    """Migrates `database` to the current schema."""

    database.create_tables([Post, Room])
