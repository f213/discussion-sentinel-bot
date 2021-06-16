import logging
import os
from telegram import Message, Update
from telegram.ext import CallbackContext, MessageHandler, Updater
from telegram.ext.filters import Filters, MessageFilter

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def delete(update: Update, context: CallbackContext):
    bot = update.message.bot

    bot.delete_message(message_id=update.message.message_id, chat_id=update.message.chat_id)


class ContainsTelegramContactFilter(MessageFilter):
    def filter(self, message: Message):
        return ' @' in message.text


class ContainsLinkFilter(MessageFilter):
    def filter(self, message: Message):
        return 'http://' in message.text or 'https://' in message.text


def in_heroku() -> bool:
    return os.getenv('HEROKU_APP_NAME', None) is not None


def main():
    bot_token = os.getenv('BOT_TOKEN')
    app_name = os.getenv('HEROKU_APP_NAME')

    bot = Updater(token=bot_token)
    bot.dispatcher.add_handler(MessageHandler(callback=delete, filters=Filters.text & ContainsTelegramContactFilter()))
    bot.dispatcher.add_handler(MessageHandler(callback=delete, filters=Filters.text & ContainsLinkFilter()))

    if not in_heroku():
        bot.start_polling()
    else:
        bot.start_webhook(
            listen='0.0.0.0',
            port=os.getenv('PORT'),
            url_path=bot_token,
            webhook_url=f'https://{app_name}.herokuapp.com/' + bot_token,
        )


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    main()
