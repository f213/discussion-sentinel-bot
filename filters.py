import operator
from functools import reduce
from telegram import Message
from telegram.ext import BaseFilter, Filters, MessageFilter
from urlextract import URLExtract

import text


class ChatMessageOnly(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.forward_from_message_id is None


def with_default_filters(*filters: BaseFilter) -> BaseFilter:
    """Apply default filters to the given filter classes"""
    default_filters = [
        Filters.text,
        ChatMessageOnly(),
    ]
    return reduce(operator.and_, [*default_filters, *filters])  # МАМА Я УМЕЮ ФУНКЦИОНАЛЬНО ПРОГРАММИРОВАТЬ


class IsMessageOnBehalfOfChat(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.sender_chat is not None


class ContainsTelegramContact(MessageFilter):
    def filter(self, message: Message) -> bool:
        return ' @' in message.text


class ContainsLink(MessageFilter):
    def __init__(self) -> None:
        self.extractor = URLExtract()

    def filter(self, message: Message) -> bool:
        return len(self.extractor.find_urls(message.text)) >= 1


class ContainsThreeOrMoreEmojies(MessageFilter):
    def filter(self, message: Message) -> bool:
        return 'three_or_more_emojies' in text.Labels(message.text)()


__all__ = [
    'ChatMessageOnly',
    'ContainsLink',
    'ContainsTelegramContact',
    'ContainsThreeOrMoreEmojies',
    'IsMessageOnBehalfOfChat',
    'with_default_filters',
]
