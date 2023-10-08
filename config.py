import yadisk
import os
from dotenv import load_dotenv, find_dotenv
from loguru import logger

logger.add('logs.log', format='{time} {level} {message}', level='DEBUG')


load_dotenv(find_dotenv())

API_TOKEN = os.getenv('API_TOKEN')
PAY_TOKEN = os.getenv('PAY_TOKEN')

ya_disk = yadisk.YaDisk(token=os.getenv('DISK_TOKEN'))
