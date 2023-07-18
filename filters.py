import operator
from functools import reduce
from telegram import Message
from telegram.ext.filters import BaseFilter, MessageFilter

import text
from helpers import DB_ENABLED


class IsNewfag(MessageFilter):

    def filter(self, message: Message) -> bool:
        if not DB_ENABLED() or message.from_user is None:
            return True

        return not self.message_is_from_oldfag(message)

    def message_is_from_oldfag(self, message: Message) -> bool:
        if int(message.from_user.id) < 10**9:  # type: ignore
            return True

        messages_count = self.messages_count(user_id=message.from_user.id, chat_id=message.chat_id)  # type: ignore
        if messages_count >= 3:
            return True

        return False

    @staticmethod
    def messages_count(user_id: int, chat_id: int) -> int:
        from models import LogEntry

        return LogEntry.select().where(
            (LogEntry.user_id == user_id),
            (LogEntry.chat_id == chat_id),
            (LogEntry.action != 'delete'),
        ).count()


class ChatMessageOnly(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.forward_from_message_id is None


def with_default_filters(*filters: BaseFilter) -> BaseFilter:
    """Apply default filters to the given filter classes"""
    default_filters = [
        ChatMessageOnly(),
        IsNewfag(),
    ]
    return reduce(operator.and_, [*default_filters, *filters])  # МАМА Я УМЕЮ ФУНКЦИОНАЛЬНО ПРОГРАММИРОВАТЬ


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
