#!/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import telegram
import logging

from ChatClient import ChatClient

# telegram imports
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi!')


# bot documentation
def help(update, context):
    update.message.reply_text("""
If you never used this bot before use /newbot command

Available commands:
/newuser - add yourself to database, to track your reading progress
/uploadfile - upload file you wish to read, available formats: pdf
/nextchunk - read next chunk of uploaded text
temp:
/uid - get your metadata
    """)


def uid(update, context):
    uid = update.message.chat.id
    cuid = ChatClient(ID=uid)

    update.message.reply_text(f"Your profile is {cuid.__dict__}", parse_mode="html")


def uploadfile(update, context):
    update.message.reply_text(f'You said: {update.message.text}')


def nextchunk(update, context):
    update.message.reply_text(f'You said: {update.message.text}')


def newuser(update, context):
    update.message.reply_text('You are being added to db')


def unknown_text(update, context):
    update.message.reply_text('Unknown command type /help to get a list of available commands')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def _add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("newuser", newuser))
    dispatcher.add_handler(CommandHandler("uploadfile", uploadfile))
    dispatcher.add_handler(CommandHandler("nextchunk", nextchunk))
    dispatcher.add_handler(CommandHandler("uid", uid))
    dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))
    dispatcher.add_error_handler(error)


def main():
    updater = Updater(BOT_TOKEN)

    _add_handlers(updater.dispatcher)

    # Start the Bot
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    updater.idle()


if __name__ == '__main__':
    main()
