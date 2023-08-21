import os
import logging

from dotenv import load_dotenv
from DBManager import MongoDBManager


if os.path.isfile('.env'):
    load_dotenv()
else:
    raise Exception("No .env file found")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("/tmp/chunk_reader_tg_bot_debug.log"), logging.StreamHandler()])


LOGGER = logging.getLogger(__name__)


BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URI = os.getenv('MONGO_DB_URI')
DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_USER_COLLECTION_NAME = os.getenv('MONGO_USER_COLLECTION_NAME')
MONGO_BOOK_COLLECTION_NAME = os.getenv('MONGO_BOOK_COLLECTION_NAME')
# optional variables for docker
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')


if not all([BOT_TOKEN, DB_NAME, MONGO_USER_COLLECTION_NAME, MONGO_BOOK_COLLECTION_NAME, MONGO_HOST]):
    raise Exception("Missing required environment variables")


MONGODBMANAGER = MongoDBManager(
    db_name=DB_NAME,
    db_user_collection_name=MONGO_USER_COLLECTION_NAME,
    db_book_collection_name=MONGO_BOOK_COLLECTION_NAME,
    username=MONGO_USERNAME,
    password=MONGO_PASSWORD,
    host=MONGO_HOST,
)
