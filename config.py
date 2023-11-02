import os
from dotenv import load_dotenv, find_dotenv
from loguru import logger

logger.add('logs.log', format='{time} {level} {message}', level='DEBUG')

TIME_ZONE = 5

load_dotenv(find_dotenv())

API_TOKEN = os.getenv('API_TOKEN')
PAY_TOKEN = os.getenv('PAY_TOKEN')
