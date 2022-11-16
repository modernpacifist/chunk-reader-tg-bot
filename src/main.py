#!/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import logging
from re import A
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


def local_files_cleanup():
    # TODO: update this to remove files not by timer, but by check if files exist
    # cleanup of local files
    # threading.Timer(30.0, local_files_cleanup).start()
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
    # metadata = update.message.chat
    # msg = mongodbmanager.insert_new_user(uid)
    msg = mongodbmanager.insert_new_user(user)
    update.message.reply_text(msg)


# bot in-chat documentation
def help(update, context) -> None:
    update.message.reply_text("""
If you have never used this bot before use /start command

Available commands:
/start - start usage with this command
/nextchunk - force next chunk of currently reading book
Not yet implemented:
/mybooks - print info about your uploaded books
/changebook - TBD
    """)


def uid(update, context) -> None:
    uid = update.message.chat.id
    cuid = ChatClient(ID=uid)

    update.message.reply_text(f"Your UID: {cuid.__dict__.get('ID')}", parse_mode="html")


# right now this function manages epub to txt conversion
def downloader(update, context) -> None:
    # this must be taken from db
    uid = update.message.chat.id
    user = mongodbmanager.find_user(uid)

    user = ChatClient(uid)

    try:
        context.bot.get_file(update.message.document).download()

        # read file
        with open(buffer_filename, 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)
            book_content = EpubManager.translateEpubToTxt(buffer_filename)
            ################################
            print(book_content)
            ################################
            # mongodbmanager.insert_book(uid, update.message.document.file_name, book_content)
            book = Book(uid, update.message.document.file_name, book_content)
            insert_success = mongodbmanager.insert_book(book)
            # must increment user total books
            if insert_success:
                user.qty_of_owned_books += 1
                user.read_progress[book.title] = 0

                mongodbmanager.update_user(user)

            else:
                update.message.reply_text("This book already exists in the database")
                return

    except Exception as e:
        update.message.reply_text(f"File was not uploaded due to internal error.\n\nDebug info:\n{str(e)}")
        # console logging
        print(e)
        return

    update.message.reply_text("Successfully uploaded a file.")


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

    files_list_message = ""
    for i, b in enumerate(owner_books, start=1):
        book = Book(b.owner_id, b.title, b.content)
        files_list_message += f"{i}: {book.title} {book.read_progress}\n"

    if files_list_message != "":
        update.message.reply_text(f"You have current books:\n{files_list_message}")
    else:
        update.message.reply_text(f"You have not uploaded any books yet")


# not exactly changebook, but cheange currently reading book
def changebook(update, context) -> None:
    uid = update.message.chat.id
    return None


# TODO: implement file upload with command
def uploadfile(update, context) -> None:
    raise NotImplementedError("Command not yet implemented")
    # update.message.reply_text(f"Command not yet implemented")
    filepath = r"C:\\Users\\vp\\Downloads\\1.tmx.epub"
    try:
        # telegram.InputFile()
        with open(filepath) as file:
            res = EpubManager.translateEpubToTxt(filepath)
            print(res)
            telegram.InputFile(file)
    except Exception as e:
        print(e)

    chat_id = update.message.chat.id
    update.message.reply_text(f'Send me EpubFile {chat_id}')


def nextchunk(update, context) -> None:
    uid = update.message.chat.id
    files = mongodbmanager.get_user_books()

    update.message.reply_text(f"You said: {uid}, {files}")


def feedchunk(update, context) -> None:
    uids = mongodbmanager.get_current_users_ids()

    res = ""
    for uid in uids:
        res += str(f"{uid.get('_id')}\n")

    update.message.reply_text(res)


# stop using the bot
def pause(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.find_user(uid)

    user = ChatClient(uid)
    user.from_dict(db_user)

    user.using_bot_flag = False

    # user.read_chunk_size = db_user.get()
    mongodbmanager.update_user(user)

    return None


def unpause(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.find_user(uid)

    user = ChatClient(uid)
    user.from_dict(db_user)

    user.using_bot_flag = True

    # user.read_chunk_size = db_user.get()
    mongodbmanager.update_user(user)

    return None


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
    dispatcher.add_handler(CommandHandler("pause", pause))
    dispatcher.add_handler(CommandHandler("unpause", unpause))

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
