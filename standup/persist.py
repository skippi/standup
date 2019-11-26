"""Module for persisting data."""

from typing import Any

from peewee import CharField, DateTimeField, Model, SqliteDatabase, Field


DB = SqliteDatabase("repo.db")


class _SnowflakeField(CharField):
    def db_value(self, value: Any) -> Any:
        if isinstance(value, int):
            return str(value)

        return value

    def python_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return int(value)

        return value


class _RoleSetField(Field):
    def db_value(self, value: Any) -> Any:
        if isinstance(value, set):
            return ",".join(str(i) for i in value)

        return value

    def python_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return set(int(s) for s in value.split(",") if s)

        return value


class _BaseModel(Model):
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


class Room(_BaseModel):
    """
    Represents a standup channel.
    """

    channel_id = _SnowflakeField()
    role_ids = _RoleSetField()


DB.connect()
DB.create_tables([Post, Room])
