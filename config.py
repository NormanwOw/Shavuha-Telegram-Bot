import os

from dotenv import load_dotenv
import aioredis
from loguru import logger

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logger.add('logs.log', format='{time} {level} {message}', level='DEBUG')

TIME_ZONE = 5

load_dotenv('.env-non-dev')

API_TOKEN = os.getenv('API_TOKEN')
PAY_TOKEN = os.getenv('PAY_TOKEN')

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')


DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SYNC_DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

redis = aioredis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)

bot = Bot(API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
