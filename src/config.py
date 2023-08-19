import os
import logging
import configparser

from dotenv import load_dotenv


if os.path.isfile('.env'):
    load_dotenv()
else:
    raise Exception("No .env file found")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("/tmp/gcsync_debug.log"), logging.StreamHandler()])


LOGGER = logging.getLogger(__name__)


BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URI = os.getenv('MONGO_DB_URI')
DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_USER_COLLECTION_NAME = os.getenv('MONGO_USER_COLLECTION_NAME')
MONGO_BOOK_COLLECTION_NAME = os.getenv('MONGO_BOOK_COLLECTION_NAME')
# optional variables for docker
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')


if not all([BOT_TOKEN, DB_URI, DB_NAME, MONGO_USER_COLLECTION_NAME, MONGO_BOOK_COLLECTION_NAME]):
    raise Exception("Missing required environment variables")


def mongo_config(filename="database.ini", section="mongo"):
    parser = configparser.ConfigParser()

    if os.path.exists(filename) is False:
        LOGGER.critical(f"config.mongo_config: {filename} does not exist")

    parser.read(filename)

    db_config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_config[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return db_config
