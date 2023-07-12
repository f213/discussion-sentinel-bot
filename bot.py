import os
from telegram import Message, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler
from telegram.ext.filters import TEXT, BaseFilter

import text
from filters import ContainsLink, ContainsTelegramContact, ContainsThreeOrMoreEmojies, IsMedia, IsMessageOnBehalfOfChat, with_default_filters
from helpers import DB_ENABLED, enable_logging, in_production, init_sentry


async def log_message(message: Message | None, action: str | None = ''):
    """Create a log entry for telegram message"""

    if message is None or not DB_ENABLED() or message.from_user is None:
        return
    from models import LogEntry

    LogEntry.create(
        user_id=message.from_user.id,
        chat_id=message.chat_id,
        message_id=message.message_id,
        text=message.text or '',
        meta={
            'tags': text.Labels(message.text)(),
        },
        raw=message.to_dict(),
        action=action,
    )


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a message"""
    message = update.message or update.edited_message

    if message is not None:
        await log_message(message, action='delete')
        await message.delete()


async def introduce_myself(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="""
Это бот, который чистит спам из телеграм-комментов. Чтобы он заработал — добавьте его как админа в дискуссионную группу канала. Не забудьте разрешить удалять сообщения.

По всем вопросам пишите fborshev@pm.me
    """,
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

    bot = Application.builder().token(bot_token).build()

    bot.add_handler(CommandHandler('start', introduce_myself))

    bot.add_handler(delete_messages_that_match(ContainsTelegramContact()))
    bot.add_handler(delete_messages_that_match(ContainsLink()))
    bot.add_handler(delete_messages_that_match(IsMessageOnBehalfOfChat()))
    bot.add_handler(delete_messages_that_match(ContainsThreeOrMoreEmojies()))
    bot.add_handler(delete_messages_that_match(IsMedia()))

    if DB_ENABLED():  # log all not handled messages
        from models import create_tables

        create_tables()  # type: ignore
        bot.add_handler(
            MessageHandler(
                filters=TEXT,
                callback=lambda update, context: log_message(update.message or update.edited_message),
            ),
        )

    if in_production():
        init_sentry()
        bot.run_webhook(
            listen='0.0.0.0',
            port=8000,
            url_path=bot_token,
            webhook_url=f'https://{app_name}.tough-dev.school/' + bot_token,
        )
    else:  # bot is running on the dev machine
        enable_logging()
        bot.run_polling()
