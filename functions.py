import json
import random
import string
import hashlib
import datetime

from aiogram import types, Bot

from order_db import OrderDB
from config import ya_disk, logger
from messages import ERROR_F

TIME_ZONE = 5


@logger.catch
def set_json(path: str, data: dict):
    json_data = get_json(path)
    json_data = json_data | data
    with open(path, 'w') as file:
        json.dump(json_data, file, ensure_ascii=False)


@logger.catch
def get_json(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)


@logger.catch
def gen_password() -> str:
    password = ''
    pw_str = string.digits+string.ascii_uppercase
    for ch in ['I', 'O', '0', 'J', 'Z', 'C']:
        pw_str = pw_str.replace(ch, '')
    length = len(pw_str)
    for i in range(5):
        password += pw_str[random.randint(0, length-1)]
    return password


@logger.catch
def update_password() -> str:
    pw = gen_password()
    pw_dict = {'employee_password': pw}
    set_json('data.json', pw_dict)
    return pw


@logger.catch
def generate_id() -> str:
    hash_data = ''
    for i in range(10):
        hash_data += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)]

    return hashlib.md5(hash_data.encode()).hexdigest()


@logger.catch
async def generate_order_number() -> int:
    order_number = random.randint(100000, 999999)
    while order_number in await OrderDB.get_order_numbers():
        order_number += 1
        if order_number > 999999:
            order_number = random.randint(100000, 999999)

    return order_number


@logger.catch
def get_time():
    now = datetime.datetime.now() + datetime.timedelta(hours=TIME_ZONE)
    time = now.strftime('%H:%M')
    hour = now.hour
    minute = now.minute

    return time, hour, minute


@logger.catch
async def get_24h_orders_list(message):
    orders_24 = await OrderDB.get_orders(1)
    if len(orders_24) == 0:
        await message.answer('Список заказов пуст')
    else:
        answer = ''
        for order_number, price, order_list, comment, date, time in orders_24:
            if comment is not None:
                comment = f'Комментарий: {comment} | '
            else:
                comment = ''
            answer += f'<b>Заказ №<u>{order_number}</u></b> | {order_list} | ' \
                      f'Оплата: {int(price)}₽ | {comment}{date} {time}\n\n'
        await message.answer(answer)


@logger.catch
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


@logger.catch
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


@logger.catch
async def error_to_db(message: types.Message, bot):
    now = datetime.datetime.now() + datetime.timedelta(hours=TIME_ZONE)
    date = now.strftime('%d.%m.%Y')
    await OrderDB.insert_error(message.from_user.full_name, message.text, date, get_time()[0])
    await bot.send_message(message.from_user.id, ERROR_F)
    await bot.send_message(5765637028, message.from_user.full_name + '\n' + message.text)


@logger.catch
async def message_filter(message: types.Message, bot: Bot, path: str):
    if message.photo:
        await message.photo[-1].download(destination_file=path)
    elif message.document:
        for file_format in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            if file_format not in message.document.file_name:
                path = None
        await message.document.download(destination_file=path)
    else:
        await message.sticker.download(destination_file=path)
    await bot.send_photo(message.from_user.id, open(path, 'rb'))
    await message.delete()
