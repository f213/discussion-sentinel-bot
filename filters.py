import operator
from functools import reduce
from telegram import Message
from telegram.ext.filters import BaseFilter, MessageFilter

import text
from helpers import DB_ENABLED


class HasNoValidPreviousMessages(MessageFilter):
    MIN_PREVIOUS_MESSAGES_COUNT = 3

    def filter(self, message: Message) -> bool:
        if not DB_ENABLED() or message.from_user is None:
            return True
        return self.has_no_valid_previous_messages(user_id=message.from_user.id, chat_id=message.chat_id)

    @classmethod
    def has_no_valid_previous_messages(cls, user_id: int, chat_id: int) -> bool:
        from models import LogEntry

        messages_count = LogEntry.select().where(
            (LogEntry.user_id == user_id),
            (LogEntry.chat_id == chat_id),
            (LogEntry.action != 'delete'),
        ).count()
        return messages_count < cls.MIN_PREVIOUS_MESSAGES_COUNT


class ChatMessageOnly(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.forward_from_message_id is None


def with_default_filters(*filters: BaseFilter) -> BaseFilter:
    """Apply default filters to the given filter classes"""
    default_filters = [
        ChatMessageOnly(),
        HasNoValidPreviousMessages(),
    ]
    very_strict_filter = [
        IsMessageOnBehalfOfChat(),
    ]
    return reduce(operator.and_, [*default_filters, *filters]) and not reduce(operator.or_, [*very_strict_filter])


class IsMessageOnBehalfOfChat(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.sender_chat is not None


class ContainsTelegramContact(MessageFilter):
    def filter(self, message: Message) -> bool:
        if message.text is None:
            return False

        return ' @' in message.text or message.text.startswith('@')


class ContainsLink(MessageFilter):

    def filter(self, message: Message) -> bool:
        if message.text is None:
            return False

        return any(entity.type in ('url', 'text_link') for entity in message.entities)


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
