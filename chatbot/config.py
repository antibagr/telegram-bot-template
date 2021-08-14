import os

from dotenv import load_dotenv
from pathlib import Path

DEBUG = os.environ.get('DEBUG', True) in (True, "True")

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))

MEDIA_ROOT = os.path.join(BASE_DIR, 'static')

SRC_DIR = os.path.join(BASE_DIR, 'src')

dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=dotenv_path, verbose=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")


ADMIN_ID = int(os.getenv("ADMIN_ID"))
MAGIC_ID = ADMIN_ID
FLOWCHAT_ID = int(os.getenv("FLOWCHAT_ID"))
ERROR_CHAT_ID = int(os.getenv("ERROR_CHAT_ID"))



TG_API_ID = int(os.getenv("TG_API_ID"))
TG_API_HASH = os.getenv("TG_API_HASH")
TELETHON_PHONE = os.getenv("TELETHON_PHONE")
APP_NAME = 'locbot_app'

PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_PORT = os.getenv("PG_PORT")


POSTGRES_URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DATABASE}"

DJANGO_SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DJANGO_DEBUG = os.getenv('DJANGO_DEBUG')
DJANGO_LANGUAGE_CODE = 'ru-ru'# 'en-us'


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_URI = F"redis://{REDIS_HOST}"
REDIS_ORDER_CHANNEL = 'orders:1'
REDIS_MESSAGE_CHANNEL = 'messages:1'

# API
# G_API_KEY=AIzaSyDBFc5iFsdmwfGtQL6IxwhiA9iQYzp2P-Y
G_API_KEY = os.getenv('G_API_KEY')
