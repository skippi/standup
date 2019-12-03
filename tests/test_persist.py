from datetime import datetime, timezone, timedelta
from functools import wraps

from peewee import SqliteDatabase
from standup.persist import Post, Room

_TEST_DB = SqliteDatabase(":memory:")
_MODELS = [Post, Room]


def use_test_database(fn):
    @wraps(fn)
    def inner(self):
        with _TEST_DB.bind_ctx(_MODELS):
            _TEST_DB.create_tables(_MODELS)
            try:
                fn(self)
            finally:
                _TEST_DB.drop_tables(_MODELS)

    return inner


class TestPost:
    @use_test_database
    def test_create(self):
        date = datetime(1970, 1, 1)
        Post.create(
            channel_id=0,
            user_id=0,
            role_ids=set(),
            timestamp=date.replace(tzinfo=timezone.utc),
        )

        result = list(Post.select())
        assert [p.timestamp for p in result] == [date]

    @use_test_database
    def test_select_expired_posts(self):
        date = datetime(1970, 1, 1, tzinfo=timezone.utc)
        Room.create(channel_id=0, role_ids=set(), cooldown=10)
        Post.create(channel_id=0, user_id=0, role_ids=set(), timestamp=date)
        Post.create(
            channel_id=0,
            user_id=0,
            role_ids=0,
            timestamp=(date + timedelta(seconds=20)),
        )

        target_time = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=11)
        assert len(Post.select_expired_posts(target_time)) == 1
