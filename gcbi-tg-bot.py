#!/usr/bin/env python

import os, logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CallbackContext, Updater, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def main() -> None:
    """Start the bot."""
    updater = Updater(os.environ.get("API_TOKEN"))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()