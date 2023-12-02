import os
from dotenv import load_dotenv
from loguru import logger

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


DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SYNC_DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'