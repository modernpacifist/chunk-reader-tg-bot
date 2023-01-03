#!/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import logging
# for local files/buffers parallel cleanup
import threading
import re
import datetime
import pytz

from Client import ChatClient
from Book import Book
from DBManager import MongoDBManager
from EpubManager import EpubManager

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

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
    uname = update.message.chat.first_name

    user = ChatClient(uid, uname)
    book_indices = mongodbmanager.get_user_books(uid)

    indices = [i.get('index') for i in book_indices]
    if indices is not None:
        user.owned_book_indices = indices

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
/changebook - change currently reading book by specifying index in the argument "/changebook <number>"
/changechunksize - change size of receiving book chunks "/changechunksize <number>"
/sharebook - make your book public for everybody "/sharebook <number>"

Admin commands:
/migrateusers - update user doc signatures
/migratebooks - update book doc signatures
""")


def migrateusers(update, context) -> None:
    # TODO: double check this code, may be dangerous

    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return
    
    user = ChatClient(uid)
    user.from_dict(db_user)

    if not user.admin:
        update.message.reply_text("You have no administrator privileges")
        return

    mongo_cursor = mongodbmanager.get_all_users()
    db_users = [i for i in mongo_cursor]
    if len(db_users) == 0:
        update.message.reply_text("No users in database")
        return 

    for db_user in db_users:
        user_uid = db_user.get('_id')
        if user_uid is None:
            update.message.reply_text(f"Problem retrieving user doc with info: {db_user}")
            continue

        user = ChatClient(db_user.get('_id'))
        user.from_dict(db_user)

        # TODO: double check this conditional, some fields may be deleted during update
        if db_user.keys() == user.__dict__.keys():
            update.message.reply_text(f"Skipped user with uid: {user_uid}")
            continue

        update_success = mongodbmanager.update_user(user)
        if update_success is False:
            update.message.reply_text(f"Problem updating user with uid: {user_uid}")
            continue

        update.message.reply_text(f"Migrated user with uid: {user_uid}")


def migratebooks(update, context) -> None:
    # TODO: double check this code, may be dangerous

    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return
    
    user = ChatClient(uid)
    user.from_dict(db_user)

    if not user.admin:
        update.message.reply_text("You have no administrator privileges")
        return

    mongo_cursor = mongodbmanager.get_all_books()
    db_books = [i for i in mongo_cursor]
    if len(db_books) == 0:
        update.message.reply_text("No books in database")
        return 

    for db_book in db_books:
        book_id = db_book.get('_id')
        if book_id is None:
            update.message.reply_text(f"Problem retrieving book doc with id: {db_book}")
            continue

        book = Book()
        book.from_dict(db_book)

        # TODO: double check this conditional, some fields may be deleted during update
        if db_book.keys() == book.__dict__.keys():
            update.message.reply_text(f"Skipped book with id: {book_id}")
            continue

        update_success = mongodbmanager.update_book(book)
        if update_success is False:
            update.message.reply_text(f"Problem updating book with id: {book_id}")
            continue

        update.message.reply_text(f"Migrated book with id: {book_id}")


def uid(update, context) -> None:
    uid = update.message.chat.id

    update.message.reply_text(f"Your UID: {uid}", parse_mode="html")


# right now this function manages epub to txt conversion
def downloader(update, context) -> None:
    # this must be taken from db
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

    user = ChatClient(uid)
    user.from_dict(db_user)

    try:
        user_doc = update.message.document
        if not user_doc.file_name.endswith(".epub"):
            update.message.reply_text("You can upload only epub files")
            return

        update.message.reply_text("Uploading...")
        current_max_book_index = mongodbmanager.get_max_book_index()

        # read file
        with open(buffer_filename, 'wb') as f:
            context.bot.get_file(user_doc).download(out=f)
            book_content = EpubManager.translateEpubToTxt(buffer_filename)
            book = Book(uid, user_doc.file_name, book_content, index=current_max_book_index, content_length=len(book_content))
            insert_success = mongodbmanager.insert_book(book)

            # must increment user total books
            if insert_success is False:
                update.message.reply_text("This book already exists in the database")
                return

            # this line is buggy
            user.qty_of_owned_books += 1

            if user.read_progress.get(book.title) is None:
                user.read_progress[book.title] = 0
            
            if book.index not in user.owned_book_indices:
                user.owned_book_indices.append(book.index)

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


# TODO: debug function/make migrate function to update db documents signatures
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
    # TODO: append a text chunk to the message with shared books with you
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

    user = ChatClient(uid)
    user.from_dict(db_user)
    # this is duplicated
    mongo_db_cursor = mongodbmanager.get_user_books(uid)
    owner_books = [item for item in mongo_db_cursor]

    shared_db_cursor = mongodbmanager.get_shared_books()
    shared_books = [item for item in shared_db_cursor]

    user_books = ""
    shared_books_message = ""
    currently_reading_string = ""
    files_list_message = ""

    current_book = None
    # TODO: use builder pattern here <14-12-22, modernpacifist> #
    try:
        for i, book in enumerate(owner_books, start=1):
            book_title = book.get('title')
            book_index = book.get('index')
            book_shared = book.get('shared')

            if None in [book_title, book_index, book_shared]:
                continue

            user_books += f"{i}: Title: \"{book_title}\" Index: {book_index} Shared: {book_shared}\n"

            book_read_progress = user.get_book_progress(book)
            if book_read_progress is not None:
                # slice removes \n at the end of default line
                user_books = user_books[:-1] + f" Completion: {book_read_progress}%\n"

            # double check this code later
            if user.current_read_target == book_index:
                current_book = book

        for i, book in enumerate(shared_books, start=1):
            book_title = book.get('title')
            book_index = book.get('index')

            if None in [book_title, book_index]:
                continue

            shared_books_message += f"{i}: Title: \"{book_title}\" Index: {book_index}\n"

            book_read_progress = user.get_book_progress(book)
            if book_read_progress is not None:
                # slice removes \n at the end of default line
                shared_books_message = shared_books_message[:-1] + f" Completion: {book_read_progress}%\n"

            if user.current_read_target == book_index:
                current_book = book

        if current_book is not None:
            # BUG: currently_reading is possibly unbound
            currently_reading_string = f"Currently reading:\nTitle: \"{current_book.get('title')}\" Index: {current_book.get('index')}\n\n"
            book_read_progress = user.get_book_progress(current_book)
            if book_read_progress is not None:
                # slice removes \n at the end of default line
                currently_reading_string = currently_reading_string[:-2] + f" Completion: {book_read_progress}%\n\n"

        if user_books != "":
            files_list_message += f"Your books:\n{user_books}\n"

        if shared_books_message != "":
            files_list_message += f"Shared books:\n{shared_books_message}\n"

        if files_list_message != "":
            update.message.reply_text(f"{currently_reading_string}{files_list_message}")
            return

        update.message.reply_text("You have not uploaded any books yet")

    except Exception as e:
        print(e)
        update.message.reply_text(f"Internal error: {str(e)}")


def renamebook(update, context):
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

    user = ChatClient(uid)
    user.from_dict(db_user)
    mongo_db_cursor = mongodbmanager.get_user_books(uid)
    owner_books = [item for item in mongo_db_cursor]

    shared_db_cursor = mongodbmanager.get_shared_books()
    shared_books = [item for item in shared_db_cursor]

    return


# not exactly changebook, but change currently reading book
def changebook(update, context) -> None:
    # TODO: add a choose index functionality out of user-owned book indices
    # TODO: add a check if book was deleted and current read target will be automatically updated with the new index

    args = context.args
    if len(args) != 1:
        update.message.reply_text(f"You must specify only one argument\nYou specified: {len(args)} arguments")
        return

    if bool(re.match(r"^([0-9]+)$", args[0])) is False:
        update.message.reply_text(f"Your argument must be a number")
        return

    try:
        new_book_index = int(args[0])
    except Exception as e:
        update.message.reply_text(str(e))
        return

    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

    user = ChatClient(uid)
    user.from_dict(db_user)
    db_book = mongodbmanager.get_book(new_book_index)

    # If book is not yours and it is not shared, then 
    if not new_book_index in user.owned_book_indices and db_book.get('shared') is False:
        update.message.reply_text(f"You do not own book with index: {new_book_index}")
        return

    # If book is shared and you're trying to read it, creates progress in your db user record
    user.current_read_target = new_book_index
    if db_book.get('shared'):
        update.message.reply_text(f"You are reading a shared book with index: {new_book_index}")
        shared_book_title = db_book.get("title")
        if user.read_progress.get(shared_book_title) is None:
            user.read_progress[shared_book_title] = 0

    mongodbmanager.update_user(user)
    update.message.reply_text(f"Current book was successfully changed")


def changechunksize(update, context) -> None:
    args = context.args
    if len(args) != 1:
        update.message.reply_text(f"You must specify only one argument\nYou specified: {len(args)}")
        return

    if bool(re.match(r"^([0-9]+)$", args[0])) is False:
        update.message.reply_text(f"Your argument must be a number")
        return

    try:
        new_chunk_size = int(args[0])
    except Exception as e:
        update.message.reply_text(str(e))
        return

    if new_chunk_size > 2000 or new_chunk_size < 1:
        update.message.reply_text("Chunk size must not exceed 4000 and be at least 1")
        return

    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

    user = ChatClient(uid)
    user.from_dict(db_user)

    user.read_chunk_size = new_chunk_size

    mongodbmanager.update_user(user)

    update.message.reply_text(f"Chunk size successfully changed")


# TODO: add a flag to book doc as {shared: true/false}
def sharebook(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

    user = ChatClient(uid)
    user.from_dict(db_user)

    args = context.args
    if len(args) != 1:
        update.message.reply_text(f"You must specify only one argument\nYou specified: {len(args)}")
        return

    if bool(re.match(r"^([0-9]+)$", args[0])) is False:
        update.message.reply_text(f"Your argument must be a number")
        return

    try:
        book_index = int(args[0])
    except Exception as e:
        update.message.reply_text(str(e))
        return

    if not book_index in user.owned_book_indices:
        update.message.reply_text(f"You do not own book with specified index {book_index}")
        return

    db_book = mongodbmanager.get_book(book_index)
    book = Book()
    book.from_dict(db_book)

    flag = mongodbmanager.update_book(book, query={"shared": True})
    if flag is True:
        update.message.reply_text(f"You successfully shared a book with index {book_index}")


def nextchunk(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

    user = ChatClient(uid)
    user.from_dict(db_user)

    db_book = mongodbmanager.get_book(user.current_read_target)
    if db_book is None:
        update.message.reply_text(f"Book with index {user.current_read_target} not found\nChange your current book")
        return

    book_content = db_book.get("content")

    # gets index of the latest chunk
    chunk_start = user.read_progress.get(db_book.get("title"))
    # this code already exists in /changebook command
    if chunk_start is None:
        user.read_progress[db_book.get("title")] = 0
        # check if this is needed
        chunk_start = 0

    # find can return -1 if the char won't be found
    chunk_end = book_content.find('.', chunk_start + user.read_chunk_size) + 1
    if chunk_end == -1:
        chunk_end = len(book_content) - 1

    # check chunk_content size
    # TODO: bug here, if indexing exceeds book_content max length
    chunk_content = book_content[chunk_start:chunk_end]
    if chunk_content is None:
        update.message.reply_text("You have finished this book")
        return

    update.message.reply_text(chunk_content)

    user.read_progress[db_book.get("title")] = chunk_end
    mongodbmanager.update_user(user)


# stop using the bot
def pause(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

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


def unpause(update, context) -> None:
    uid = update.message.chat.id
    db_user = mongodbmanager.get_user(uid)
    if db_user is None:
        update.message.reply_text("You are not in database, begin use with /start command")
        return

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
    update.message.reply_text("Unknown command type /help to get a list of available commands")


def error(update, context) -> None:
    logger.warning(f"Update {update} caused error {context.error}")


def feedchunk(context: CallbackContext):
    # logger.info(f"Time: {datetime} Executing feedchunk command")
    # send message to all users
    mongo_current_users_cursor = mongodbmanager.get_current_users_ids()
    current_users_ids = [i.get('_id') for i in mongo_current_users_cursor]

    for uid in current_users_ids:
        if uid is None:
            continue

        db_user = mongodbmanager.get_user(uid)

        if db_user is None:
            print(f"User {uid} is not in database")
            continue

        user = ChatClient(uid)
        user.from_dict(db_user)

        db_book = mongodbmanager.get_book(user.current_read_target)
        if db_book is None:
            print(f"User {uid} does not have access to this book")
            continue

        book_content = db_book.get("content")

        # gets index of the latest chunk
        chunk_start = user.read_progress.get(db_book.get("title"))
        # this code already exists in /changebook command
        if chunk_start is None:
            user.read_progress[db_book.get("title")] = 0
            # check if this is needed
            chunk_start = 0

        # find can return -1 if the char won't be found
        chunk_end = book_content.find('.', chunk_start + user.read_chunk_size) + 1
        if chunk_end == -1:
            chunk_end = len(book_content) - 1

        # check chunk_content size
        # TODO: bug here, if indexing exceeds book_content max length
        chunk_content = book_content[chunk_start:chunk_end]
        if chunk_content is None:
            update.message.reply_text("You have finished this book")
            continue
            # return

        # update.message.reply_text(chunk_content)
        context.bot.send_message(chat_id=user._id, text=chunk_content)

        user.read_progress[db_book.get("title")] = chunk_end
        mongodbmanager.update_user(user)

        # chunk = 
        # user_id = 777855967


def _add_handlers(dispatcher) -> None:
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("start", start, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("mybooks", mybooks))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("nextchunk", nextchunk))
    dispatcher.add_handler(CommandHandler("changebook", changebook, pass_args=True))
    dispatcher.add_handler(CommandHandler("changechunksize", changechunksize, pass_args=True))
    dispatcher.add_handler(CommandHandler("sharebook", sharebook, pass_args=True))
    dispatcher.add_handler(CommandHandler("uid", uid))
    dispatcher.add_handler(CommandHandler("update", update))
    dispatcher.add_handler(CommandHandler("pause", pause))
    dispatcher.add_handler(CommandHandler("unpause", unpause))
    dispatcher.add_handler(CommandHandler("migrateusers", migrateusers))
    dispatcher.add_handler(CommandHandler("migratebooks", migratebooks))

    dispatcher.add_handler(MessageHandler(filters.Filters.text, unknown_text))
    dispatcher.add_handler(MessageHandler(filters.Filters.document, downloader))
    dispatcher.add_error_handler(error)


def main():
    try:
        updater = Updater(BOT_TOKEN)
    except Exception as e:
        print(e)
        exit(1)

    local_files_cleanup()

    j = updater.job_queue
    # j.run_repeating(feedchunk, 10)
    # j.run_repeating(feedchunk, 60)
    j.run_daily(feedchunk,
        days=(0, 1, 2, 3, 4, 5, 6),
        time=datetime.time(hour=10, minute=00, second=00, tzinfo=pytz.timezone('Europe/Moscow'))
    )
    # job_daily.run()

    # _add_handlers line is essenstial for command handling
    _add_handlers(updater.dispatcher)

    # Start the Bot
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    updater.idle()


if __name__ == "__main__":
    main()
