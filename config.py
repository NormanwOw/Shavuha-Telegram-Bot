import yadisk
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_TOKEN = os.getenv('API_TOKEN')
PAY_TOKEN = os.getenv('PAY_TOKEN')

ya_disk = yadisk.YaDisk(token=os.getenv('DISK_TOKEN'))
