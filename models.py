import os
import peewee as pw
from playhouse.db_url import connect
from playhouse.postgres_ext import JSONField

db = connect(os.getenv('DATABASE_URL'))


class LogEntry(pw.Model):
    user_id = pw.BigIntegerField()
    chat_id = pw.BigIntegerField()
    message_id = pw.BigIntegerField()
    action = pw.CharField(default='')
    text = pw.CharField()
    meta = JSONField()
    raw = JSONField()

    class Meta:
        database = db
        indexes = (
            ('chat_id', 'message_id'),
            True,
        )


def create_tables():
    db.create_tables([LogEntry])
