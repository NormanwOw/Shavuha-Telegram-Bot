import os
import sqlite3
import datetime

from config import TIME_ZONE


class SiteDB:

    if os.name == 'nt':
        path = '..\shava-site\shava\db.sqlite3'
    else:
        path = '../../var/www/shava-site/shava/db.sqlite3'

    __connection = sqlite3.connect(path)
    __cursor = __connection.cursor()

    @classmethod
    async def insert_order(cls, order_number: str or int, date: str, time: str):
        num = str(order_number)
        with cls.__connection:
            cls.__cursor.execute("INSERT INTO shavuha_orders (order_number, date, time) VALUES (?, ?, ?)",
                                 (num, date, time))

    @classmethod
    async def get_orders(cls):
        with cls.__connection:
            return cls.__cursor.execute("SELECT * FROM shavuha_orders").fetchall()

    @classmethod
    async def delete_expired_orders(cls):
        now = datetime.datetime.now() + datetime.timedelta(hours=TIME_ZONE)
        orders_list = await cls.get_orders()

        for order in orders_list:
            date_time = datetime.datetime.strptime(f'{order[2]} {order[3]}', '%d.%m.%Y %H:%M')
            expire = date_time + datetime.timedelta(hours=1)
            if now > expire:
                with cls.__connection:
                    return cls.__cursor.execute("DELETE FROM shavuha_orders WHERE order_number = ?", (order[1],))
