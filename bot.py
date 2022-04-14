from typing import Optional

import os
from telegram import Message, Update
from telegram.ext import CallbackContext, Dispatcher, MessageHandler, Updater
from telegram.ext.filters import BaseFilter, Filters

import rekognition
import text
from filters import ContainsLink, ContainsTelegramContact, IsMessageOnBehalfOfChat, with_default_filters
from helpers import DB_ENABLED, enable_logging, in_production, init_sentry


def get_profile_picture(message: Message) -> Optional[str]:
    photos = message.from_user.get_profile_photos()

    if photos is not None and photos.total_count > 0:
        profile_picture = photos.photos[0][0].get_file()
        return profile_picture.file_path


def log_message(message: Message, action: Optional[str] = ''):
    """Create a log entry for telegram message"""

    if message is None or not DB_ENABLED():
        return
    from models import LogEntry

    LogEntry.create(
        user_id=message.from_user.id,
        chat_id=message.chat_id,
        message_id=message.message_id,
        text=message.text,
        meta={
            'tags': [
                *rekognition.get_labels(image_url=get_profile_picture(message)),
                *text.Labels(message.text)(),
            ],
        },
        raw=message.to_dict(),
        action=action,
    )


def delete(update: Update, context: CallbackContext):
    message = update.message or update.edited_message

    log_message(message, action='delete')
    message.bot.delete_message(
        message_id=message.message_id,
        chat_id=message.chat_id,
    )


def delete_messages_that_match(*filters: BaseFilter) -> MessageHandler:
    """Sugar for quick adding delete message callbacks"""
    return MessageHandler(callback=delete, filters=with_default_filters(*filters))


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        raise RuntimeError('Please set BOT_TOKEN environment variable')
    app_name = os.getenv('BOT_NAME')

    bot = Updater(token=bot_token)
    dispatcher: Dispatcher = bot.dispatcher  # type: ignore

    dispatcher.add_handler(delete_messages_that_match(ContainsTelegramContact()))
    dispatcher.add_handler(delete_messages_that_match(ContainsLink()))
    dispatcher.add_handler(delete_messages_that_match(IsMessageOnBehalfOfChat()))

    if DB_ENABLED():  # log all not handled messages
        from models import create_tables
        create_tables()  # type: ignore
        dispatcher.add_handler(
            MessageHandler(filters=Filters.text, callback=lambda update, context: log_message(update.message or update.edited_message)),
        )

    if in_production():
        init_sentry()
        bot.start_webhook(
            listen='0.0.0.0',
            port=8000,
            url_path=bot_token,
            webhook_url=f'https://{app_name}.tough-dev.school/' + bot_token,
        )
        bot.idle()
    else:  # bot is running on the dev machine
        enable_logging()
        bot.start_polling()
