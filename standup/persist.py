"""Module for persisting data."""

from typing import Any

from peewee import CharField, DateTimeField, Model, SqliteDatabase, Field


DB = SqliteDatabase("repo.db")


class SnowflakeField(CharField):
    def db_value(self, value: Any) -> Any:
        if isinstance(value, int):
            return str(value)

        return value

    def python_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return int(value)

        return value


class RoleSetField(Field):
    def db_value(self, value: Any) -> Any:
        if isinstance(value, set):
            return ",".join(str(i) for i in value)

        return value

    def python_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return set(int(s) for s in value.split(",") if s)

        return value


class BaseModel(Model):
    class Meta:
        database = DB


class Post(BaseModel):
    """
    Represents an active standup post.

    Posts are active if their age is less than 24 hours.
    """

    channel_id = SnowflakeField()
    user_id = SnowflakeField()
    role_ids = RoleSetField()
    timestamp = DateTimeField()


class Room(BaseModel):
    """
    Represents a standup channel.
    """

    channel_id = SnowflakeField()
    role_ids = RoleSetField()


DB.connect()
DB.create_tables([Post, Room])
