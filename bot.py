import logging
import os
from telegram import Message, Update
from telegram.ext import CallbackContext, MessageHandler, Updater
from telegram.ext.filters import Filters, MessageFilter
from urlextract import URLExtract


def get_message(update: Update) -> Message:
    return update.message or update.edited_message


def delete(update: Update, context: CallbackContext):
    message = get_message(update)

    message.bot.delete_message(
        message_id=message.message_id,
        chat_id=message.chat_id,
    )


class ContainsTelegramContactFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return ' @' in message.text


class ContainsLinkFilter(MessageFilter):
    def __init__(self):
        self.extractor = URLExtract()

    def filter(self, message: Message) -> bool:
        return len(self.extractor.find_urls(message.text)) >= 1


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
        bot.idle()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    if not in_heroku():
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        )

    main()
