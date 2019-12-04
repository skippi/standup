"""Module for persisting data."""

from datetime import datetime, timezone
from typing import Any, Set

from peewee import (
    CharField,
    DateTimeField,
    IntegerField,
    Field,
    ForeignKeyField,
    Model,
    SqliteDatabase,
)


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

    Posts are active if their age is less than the room's cooldown.
    """

    channel_id = _SnowflakeField()
    user_id = _SnowflakeField()
    role_ids = _RoleSetField()
    timestamp = DateTimeField()
    message_id = _SnowflakeField()

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
    cooldown = IntegerField(default=86400)

    def format_for_listing(self) -> str:
        """Formats the Room for the `rooms list` command."""

        roles_query = RoomRole.select().where(RoomRole.room == self.id)
        role_ids = set(r.role_id for r in roles_query)
        roles_str = str(role_ids) if role_ids else "{}"
        return f"{self.channel_id} | Cooldown: {self.cooldown} | Roles: {roles_str}"

    def update_roles(self, role_ids: Set[int]):
        """Updates the roles by setting values"""

        roles_to_add = [RoomRole(room=self, role_id=role_id) for role_id in role_ids]
        RoomRole.delete().where(RoomRole.room == self).execute()
        RoomRole.bulk_create(roles_to_add)


class RoomRole(_BaseModel):
    """Represents a room's assigned roles"""

    room = ForeignKeyField(Room)
    role_id = _SnowflakeField()


def migrate(database: SqliteDatabase):
    """Migrates `database` to the current schema."""

    database.create_tables([Post, Room])
