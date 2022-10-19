#!/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import logging
from textwrap import shorten
import telegram
import numpy as np

from Client import ChatClient
from DBManager import MongoDBManager
from EpubManager import EpubManager

# telegram imports
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URI = os.getenv('MONGO_DB_URI')
DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_USER_COLLECTION_NAME = os.getenv('MONGO_USER_COLLECTION_NAME')
MONGO_TEXT_COLLECTION_NAME = os.getenv('MONGO_TEXT_COLLECTION_NAME')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

mongodbmanager = MongoDBManager(
    db_uri=DB_URI,
    db_name=DB_NAME,
    db_user_collection_name=MONGO_USER_COLLECTION_NAME,
    db_text_collection_name=MONGO_TEXT_COLLECTION_NAME,
)


def start(update, context):
    uid = update.message.chat.id
    # metadata = update.message.chat
    mongodbmanager.insert_new_user(uid)


# bot documentation
def help(update, context):
    update.message.reply_text("""
If you have never used this bot before use /start command

Available commands:
/uploadfile - upload file you wish to read, available formats: pdf
/nextchunk - read next chunk of uploaded text
temp:
/uid - get your metadata
/myfiles - get your uploaded books
    """)


def uid(update, context):
    uid = update.message.chat.id
    cuid = ChatClient(ID=uid)

    update.message.reply_text(f"Your UID: {cuid.__dict__.get('ID')}", parse_mode="html")
    logger.level


# right now this function manages epub to txt conversion
def downloader(update, context):
    # receive file
    try:
        context.bot.get_file(update.message.document).download()
        update.message.reply_text("uploaded a file")
    except Exception as e:
        update.message.reply_text(e)
        exit(1)

    buffer_filename = "filename.buffer"

    # read file
    with open(buffer_filename, 'wb') as f:
        context.bot.get_file(update.message.document).download(out=f)
        text = EpubManager.translateEpubToTxt(buffer_filename)
        uid = update.message.chat.id
        mongodbmanager.insert_text_data(uid, update.message.document.file_name, text)

    try:
        for file in os.listdir():
            if file.endswith(".epub") or file.endswith(".buffer"):
                os.remove(file)
    except Exception as e:
        print(e)
        pass


def myfiles(update, context):
    uid = update.message.chat.id
    files = mongodbmanager.get_owner_files(uid)

    if files is None:
        update.message.reply_text(f"You have not uploaded any files yet")
    else:
        files_list_message = ""
        for f in files:
            files_list_message += f"{f.get('BookTitle')}\n"
        update.message.reply_text(f"You have current books:\n{files_list_message}")


def uploadfile(update, context):
    # filepath = r"C:\\Users\\vp\\Downloads\\1.tmx.epub"
    try:
        telegram.InputFile()
        # with open(filepath) as file:
            # res = EpubManager.translateEpubToTxt(filepath)
            # print(res)
            # telegram.InputFile(file)
    except Exception as e:
        print(e)

    chat_id = update.message.chat.id
    update.message.reply_text(f'Send me EpubFile {chat_id}')


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
    dispatcher.add_handler(CommandHandler("myfiles", myfiles))
    dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))
    dispatcher.add_handler(MessageHandler(Filters.document, downloader))
    dispatcher.add_error_handler(error)


def main():
    try:
        updater = Updater(BOT_TOKEN)
    except Exception as e:
        print(e)
        exit(1)


    _add_handlers(updater.dispatcher)

    # Start the Bot
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    updater.idle()


if __name__ == '__main__':
    main()
