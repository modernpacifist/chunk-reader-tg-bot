import os

from dotenv import load_dotenv


if os.path.isfile('.env'):
    load_dotenv()
else:
    raise Exception("No .env file found")

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URI = os.getenv('MONGO_DB_URI')
DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_USER_COLLECTION_NAME = os.getenv('MONGO_USER_COLLECTION_NAME')
MONGO_BOOK_COLLECTION_NAME = os.getenv('MONGO_BOOK_COLLECTION_NAME')

if not all([BOT_TOKEN, DB_URI, DB_NAME, MONGO_USER_COLLECTION_NAME, MONGO_BOOK_COLLECTION_NAME]):
    raise Exception("Missing required environment variables")
