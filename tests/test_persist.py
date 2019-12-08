from datetime import datetime, timezone, timedelta
from functools import wraps

from peewee import SqliteDatabase
from standup.persist import Post, Room, RoomRole, MODELS, initialize


_TEST_DB = SqliteDatabase(":memory:")


def use_test_database(fn):
    @wraps(fn)
    def inner(self):
        with _TEST_DB.bind_ctx(MODELS):
            initialize(_TEST_DB)
            try:
                fn(self)
            finally:
                _TEST_DB.drop_tables(MODELS)

    return inner


def test_initialize():
    test_db = SqliteDatabase(":memory:")
    with test_db.bind_ctx(MODELS):
        initialize(test_db)
        assert test_db.get_tables() == [t._meta.table_name for t in MODELS]


class TestPost:
    @use_test_database
    def test_create(self):
        date = datetime(1970, 1, 1)
        room = Room.create(channel_id=0)
        Post.create(
            room=room,
            user_id=0,
            timestamp=date.replace(tzinfo=timezone.utc),
            message_id=0,
        )

        assert [p.timestamp for p in Post.select()] == [date]

    @use_test_database
    def test_is_expired(self):
        date = datetime(1970, 1, 1, tzinfo=timezone.utc)
        room = Room.create(channel_id=0, cooldown=10)
        Post.create(room=room, user_id=0, timestamp=date, message_id=0)
        Post.create(
            room=room,
            user_id=0,
            timestamp=(date + timedelta(seconds=20)),
            message_id=0,
        )

        target_time = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=11)
        result = Post.select().join(Room).where(Post.is_expired(target_time))
        assert len(result) == 1


class TestRoom:
    @use_test_database
    def test_format_for_listing(self):
        room = Room.create(channel_id=0, cooldown=10)
        assert room.format_for_listing() == "0 | Cooldown: 10 | Roles: {}"

    @use_test_database
    def test_format_for_listing_lists_roles(self):
        room = Room.create(channel_id=0, cooldown=10)
        RoomRole.bulk_create(
            [RoomRole(room=room, role_id=12312321), RoomRole(room=room, role_id=123812)]
        )

        assert (
            room.format_for_listing() == "0 | Cooldown: 10 | Roles: {12312321, 123812}"
        )

    @use_test_database
    def test_update_roles(self):
        room = Room.create(channel_id=0, cooldown=10)
        room.update_roles({1, 2, 3})

        result = set(r.role_id for r in RoomRole.select().where(RoomRole.room == room))
        assert result == {1, 2, 3}
