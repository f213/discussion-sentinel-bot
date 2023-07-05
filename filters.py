import operator
from functools import reduce
from telegram import Message
from telegram.ext import BaseFilter, MessageFilter

import text
from helpers import DB_ENABLED

MIN_PREVIOUS_MESSAGES_COUNT = 3


def is_fake_user(user_id: int) -> bool:
    from models import LogEntry

    messages_count = LogEntry.select().where((LogEntry.user_id == user_id) & (LogEntry.action != 'delete')).count()
    return messages_count < MIN_PREVIOUS_MESSAGES_COUNT


class ChatMessageOnly(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.forward_from_message_id is None


def with_default_filters(*filters: BaseFilter) -> BaseFilter:
    """Apply default filters to the given filter classes"""
    default_filters = [
        ChatMessageOnly(),
    ]
    return reduce(operator.and_, [*default_filters, *filters])  # МАМА Я УМЕЮ ФУНКЦИОНАЛЬНО ПРОГРАММИРОВАТЬ


class IsMessageOnBehalfOfChat(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.sender_chat is not None


class ContainsTelegramContact(MessageFilter):
    def filter(self, message: Message) -> bool:
        if message.text is None:
            return False  # type: ignore

        return ' @' in message.text or message.text.startswith('@')


class ContainsLink(MessageFilter):

    def filter(self, message: Message) -> bool:
        if message.text is None:
            return False  # type: ignore

        entities_types = set([entity.type for entity in message.entities])
        has_links = len(entities_types.intersection({'url', 'text_link'})) != 0

        if DB_ENABLED() and has_links:
            return is_fake_user(message.from_user.id)

        return has_links


class ContainsThreeOrMoreEmojies(MessageFilter):
    def filter(self, message: Message) -> bool:
        return 'three_or_more_emojies' in text.Labels(message.text)()


class IsMedia(MessageFilter):
    def filter(self, message: Message) -> bool:
        if any([message.document, message.audio, message.voice, message.video_note]):
            return True

        if len(message.photo) > 0:
            return True

        return False


__all__ = [
    'ChatMessageOnly',
    'ContainsLink',
    'ContainsTelegramContact',
    'ContainsThreeOrMoreEmojies',
    'IsMessageOnBehalfOfChat',
    'with_default_filters',
]
