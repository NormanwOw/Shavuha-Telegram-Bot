import json
import random
import string
import hashlib
import datetime

from aiogram import Bot

from order_db import OrderDB
from config import ya_disk

TIME_ZONE = 5


def set_json(path: str, users: dict):
    with open(path, 'w') as file:
        json.dump(users, file, ensure_ascii=False)


def get_json(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)


def gen_password() -> str:
    password = ''
    pw_str = string.digits+string.ascii_uppercase
    for ch in ['I', 'O', '0', 'J', 'Z', 'C']:
        pw_str = pw_str.replace(ch, '')
    length = len(pw_str)
    for i in range(5):
        password += pw_str[random.randint(0, length-1)]
    return password


def update_password() -> str:
    pw = gen_password()
    pw_dict = {'employee_password': pw}
    set_json('data.json', pw_dict)
    return pw


def generate_id() -> str:
    hash_data = ''
    for i in range(10):
        hash_data += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)]

    return hashlib.md5(hash_data.encode()).hexdigest()


async def generate_order_number() -> int:
    order_number = random.randint(100000, 999999)
    while order_number in await OrderDB.get_order_numbers():
        order_number += 1
        if order_number > 999999:
            order_number = random.randint(100000, 999999)

    return order_number


def get_time():
    now = datetime.datetime.now() + datetime.timedelta(hours=TIME_ZONE)
    time = now.strftime('%H:%M')
    hour = now.hour
    minute = now.minute

    return time, hour, minute


async def get_24h_orders_list(message):
    orders_24 = await OrderDB.get_orders_24h()
    if len(orders_24) == 0:
        await message.answer('Список заказов пуст')
    else:
        order = ''
        answer = ''
        for order_number, price, order_list, comment, date, time in orders_24:
            if comment is not None:
                comment = f'Комментарий: {comment} | '
            else:
                comment = ''
            order_list = json.loads(order_list.replace('\'', '"'))

            for product in order_list:
                order += f'{product}: {order_list[product]} '
            answer += f'<b>Заказ №<u>{order_number}</u></b> | {order}| ' \
                      f'Оплата: {int(price)}₽ | {comment}{date} {time}\n\n'
        await message.answer(answer)


async def send_order_to_employees(comment: str, order_list: str, bot: Bot, order_number: int, user_time_str: str,
                                  price: int, date: str, time: str):
    if comment is None:
        comm = ''
    else:
        comm = f'\n\n✏ Комментарий: {comment}'

    order = json.loads(order_list.replace('\'', '"'))
    order_str = ''
    for employee in await OrderDB.get_id_by_status('Повар'):
        for product in order:
            order_str += f'\n ▫️ {product}: {order[product]}'
        await bot.send_message(employee,
                               f'<b>Заказ №<u>{order_number}</u></b>'+user_time_str+order_str+f'\n'
                               f'__________\n'
                               f'{price}₽'+comm+f'\n\n'
                               f'{date} {time}')


async def backup(date):
    data = get_json('data.json')
    last_backup = data['backup']
    d = datetime.datetime.strptime(last_backup, '%d.%m.%Y')
    t = datetime.datetime.today()
    delta = d - t
    if delta.days < -3:
        ya_disk.remove('/database.db')
        ya_disk.upload('database.db', '/database.db')
        data['backup'] = date
        set_json('data.json', data)
