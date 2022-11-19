#!/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import logging
# for local files/buffers parallel cleanup
import threading

from Client import ChatClient
from Book import Book
from DBManager import MongoDBManager
from EpubManager import EpubManager
    
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URI = os.getenv('MONGO_DB_URI')
DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_USER_COLLECTION_NAME = os.getenv('MONGO_USER_COLLECTION_NAME')
MONGO_BOOK_COLLECTION_NAME = os.getenv('MONGO_BOOK_COLLECTION_NAME')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

mongodbmanager = MongoDBManager(
    db_uri=DB_URI,
    db_name=DB_NAME,
    db_user_collection_name=MONGO_USER_COLLECTION_NAME,
    db_book_collection_name=MONGO_BOOK_COLLECTION_NAME,
)

# sample local buffer filename used to download 
buffer_filename = "filename.buffer"

# # beta keyboard
# en_options1 = telegram.KeyboardButton('sample1')
# en_options2 = telegram.KeyboardButton('sample2')
# en_options3 = telegram.KeyboardButton('sample3')
# en_options4 = telegram.KeyboardButton('sample4')
# en_options_kb = telegram.ReplyKeyboardMarkup([[en_options1, en_options2], [en_options3, en_options4]], resize_keyboard=True, one_time_keyboard=True)


def local_files_cleanup():
    # TODO: update this to remove files not by timer, but by check if files exist
    # cleanup of local files
    threading.Timer(30.0, local_files_cleanup).start()
    try:
        for file in os.listdir():
            if file.endswith(".epub") or file.endswith(".buffer"):
                os.remove(file)
                print("Local files cleaned up")
    except Exception as e:
        print(e)


# tg functions start from here
def start(update, context) -> None:
    # TODO: start must have a check if user already exists in db
    uid = update.message.chat.id
    user = ChatClient(uid)
    msg = mongodbmanager.insert_new_user(user)
    update.message.reply_text(msg)


# bot in-chat documentation
def help(update, context) -> None:
    update.message.reply_text("""
If you have never used this bot before use /start command

Available commands:
/start - start usage with this command
/nextchunk - force next chunk of currently reading book
/mybooks - print info about your uploaded books
/pause - pause usage of the bot, you will stop receiving book chunks
/unpause - unpause usage of the bot, you will start receiving book chunks regularly

Not yet implemented:
/changebook - TBD
    """)


def uid(update, context) -> None:
    uid = update.message.chat.id

    update.message.reply_text(f"Your UID: {uid}", parse_mode="html")


# right now this function manages epub to txt conversion
def downloader(update, context) -> None:
    # this must be taken from db
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    user = ChatClient(uid)
    user.from_dict(db_user)

    try:
        update.message.reply_text("Uploading...")
        current_max_book_index = mongodbmanager.get_max_book_index()
        context.bot.get_file(update.message.document).download()

        # read file
        with open(buffer_filename, 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)
            book_content = EpubManager.translateEpubToTxt(buffer_filename)
            book = Book(uid, update.message.document.file_name, book_content, index=current_max_book_index, content_length=len(book_content))
            insert_success = mongodbmanager.insert_book(book)
            # must increment user total books

            if insert_success is False:
                update.message.reply_text("This book already exists in the database")
                return

            # this line is buggy
            user.qty_of_owned_books += 1
            user.read_progress[book.title] = 0

            # check if this is the first book user uploads
            if user.current_read_target is None:
                user.current_read_target = book.index

            mongodbmanager.update_user(user)

    except Exception as e:
        update.message.reply_text(f"File was not uploaded due to internal error.\n\nDebug info:\n{str(e)}")
        # console logging
        print(e)
        return

    update.message.reply_text("Successfully uploaded the book.")


# debug function
def update(update, context) -> None:
    uid = update.message.chat.id
    user = ChatClient(uid)
    user.current_read_target = 0

    try:
        mongodbmanager.update_user(user)

    except Exception as e:
        print(e)

    finally:
        update.message.reply_text("User was successfully updated")


def mybooks(update, context) -> None:
    uid = update.message.chat.id
    owner_books = mongodbmanager.get_user_books(uid)


    db_user = mongodbmanager.get_user(uid)
    user = ChatClient(uid)
    user.from_dict(db_user)

    try:
        files_list_message = ""
        for i, book in enumerate(owner_books, start=1):
            files_list_message += f"{i}: {book.get('title')} index: {book.get('index')}\n"

            progress = user.get_book_progress(book)
            if progress is not None:
                files_list_message = files_list_message[:-1] + f" completion: {progress}%\n"



        if files_list_message != "":
            update.message.reply_text(f"You have current books:\n{files_list_message}")
        else:
            update.message.reply_text(f"You have not uploaded any books yet")

    except Exception as e:
        update.message.reply_text(f"Internal error: {str(e)}")


# not exactly changebook, but change currently reading book
def changebook(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    user = ChatClient(uid)
    user.from_dict(db_user)

    user.current_read_target = 2

    mongodbmanager.update_user(user)

    update.message.reply_text(f"Reply with the index of the book you want to read now:")


def nextchunk(update, context) -> None:
    uid = update.message.chat.id

    db_user = mongodbmanager.get_user(uid)
    user = ChatClient(uid)
    user.from_dict(db_user)

    db_book = mongodbmanager.get_current_book(user.current_read_target)

    book_content = db_book.get("content")

    # gets index of the latest chunk
    chunk_start = user.read_progress[db_book.get('title')]
    # find can return -1 if the char won't be found
    chunk_end = book_content.find('.', chunk_start + user.read_chunk_size) + 1
    if chunk_end == -1:
        chunk_end = len(book_content) - 1
    chunk_content = book_content[chunk_start:chunk_end]

    update.message.reply_text(chunk_content)

    user.read_progress[db_book.get('title')] = chunk_end
    mongodbmanager.update_user(user)


def feedchunk(update, context) -> None:
    uids = mongodbmanager.get_current_users_ids()

    res = ""
    for uid in uids:
        res += str(f"{uid.get('_id')}\n")

    update.message.reply_text(res)


# stop using the bot
def freeze(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)

    user = ChatClient(uid)
    user.from_dict(db_user)

    # check if user already paused its subscription
    if user.using_bot_flag is True:
        user.using_bot_flag = False

        flag = mongodbmanager.update_user(user)
        if flag is True:
            update.message.reply_text("You successfully paused your subscription.\nYou will stop receiving book chunks.")
    else:
        update.message.reply_text("You already paused your subscription")


def unfreeze(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)

    user = ChatClient(uid)
    user.from_dict(db_user)

    # check if user already unpaused its subscription
    if user.using_bot_flag is False:
        user.using_bot_flag = True

        flag = mongodbmanager.update_user(user)
        if flag is True:
            update.message.reply_text("You successfully unpaused your subscription.\nYou will start receiving book chunks.")
    else:
        update.message.reply_text("You already unpaused your subscription")


def unknown_text(update, context) -> None:
    update.message.reply_text('Unknown command type /help to get a list of available commands')


def error(update, context) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def _add_handlers(dispatcher) -> None:
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("mybooks", mybooks))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("nextchunk", nextchunk))
    dispatcher.add_handler(CommandHandler("changebook", changebook))
    dispatcher.add_handler(CommandHandler("uid", uid))
    dispatcher.add_handler(CommandHandler("update", update))
    dispatcher.add_handler(CommandHandler("pause", freeze))
    dispatcher.add_handler(CommandHandler("unpause", unfreeze))

    # this command must be automatic
    dispatcher.add_handler(CommandHandler("feedchunk", feedchunk))

    dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))
    dispatcher.add_handler(MessageHandler(Filters.document, downloader))
    dispatcher.add_error_handler(error)


def main():
    try:
        updater = Updater(BOT_TOKEN)
    except Exception as e:
        print(e)
        exit(1)

    local_files_cleanup()

    # _add_handlers line is essenstial for command handling
    _add_handlers(updater.dispatcher)

    # Start the Bot
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    updater.idle()


if __name__ == '__main__':
    main()
