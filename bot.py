import logging
import operator
import os
from functools import reduce
from telegram import Message, Update
from telegram.ext import CallbackContext, MessageHandler, Updater
from telegram.ext.filters import Filters, MessageFilter
from urlextract import URLExtract


def get_message(update: Update) -> Message:
    return update.message or update.edited_message


def delete(update: Update, context: CallbackContext):
    message = get_message(update)
    if message is None:
        return

    message.bot.delete_message(
        message_id=message.message_id,
        chat_id=message.chat_id,
    )


class ContainsTelegramContact(MessageFilter):
    def filter(self, message: Message) -> bool:
        return ' @' in message.text


class ContainsLink(MessageFilter):
    def __init__(self):
        self.extractor = URLExtract()

    def filter(self, message: Message) -> bool:
        return len(self.extractor.find_urls(message.text)) >= 1


class ChatMessageOnly(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.forward_from_message_id is None


def with_default_filters(*filters):
    """Apply default filters to the given filter classes"""
    default_filters = [
        Filters.text,
        ChatMessageOnly(),
    ]
    return reduce(operator.and_, [*default_filters, *filters])  # МАМА Я УМЕЮ ФУНКЦИОНАЛЬНО ПРОГРАММИРОВАТЬ


def delete_messages_that_match(*filters) -> MessageHandler:
    """Sugar for quick adding delete message callbacks"""
    return MessageHandler(callback=delete, filters=with_default_filters(*filters))


def in_heroku() -> bool:
    return os.getenv('HEROKU_APP_NAME', None) is not None


def enable_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def main():
    bot_token = os.getenv('BOT_TOKEN')
    app_name = os.getenv('HEROKU_APP_NAME')

    bot = Updater(token=bot_token)
    bot.dispatcher.add_handler(
        delete_messages_that_match(ContainsTelegramContact()),
    )
    bot.dispatcher.add_handler(
        delete_messages_that_match(ContainsLink()),
    )

    if not in_heroku():
        enable_logging()
        bot.start_polling()

    else:
        bot.start_webhook(
            listen='0.0.0.0',
            port=os.getenv('PORT'),
            url_path=bot_token,
            webhook_url=f'https://{app_name}.herokuapp.com/' + bot_token,
        )
        bot.idle()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    main()
