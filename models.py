import os
import peewee as pw
from playhouse.db_url import connect
from playhouse.postgres_ext import JSONField

database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise RuntimeError('Please set BOT_TOKEN environment variable')
db = connect(database_url)


class LogEntry(pw.Model):
    user_id = pw.BigIntegerField()
    chat_id = pw.BigIntegerField()
    message_id = pw.BigIntegerField()
    action = pw.CharField(default='')
    text = pw.TextField()
    meta = JSONField()
    raw = JSONField()

    class Meta:
        database = db
        indexes = (
            (
                ('chat_id', 'message_id'),
                True,
            ),
        )


def create_tables():
    db.create_tables([LogEntry])


def drop_tables():
    db.drop_tables([LogEntry])
