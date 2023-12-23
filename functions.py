import json
import random
import string
import hashlib
import datetime

from aiogram import types
from asyncio import sleep
from aiofile import async_open

from order_db import OrderDB
from config import TIME_ZONE, logger
from messages import ERROR_F


@logger.catch
async def set_json(path: str, data: dict):
    json_data = await get_json(path)
    json_data = json_data | data
    async with async_open(path, 'w') as file:
        await file.write(json.dumps(json_data))


@logger.catch
async def get_json(path: str) -> dict:
    async with async_open(path, 'r') as file:
        return json.loads(await file.read())


@logger.catch
async def gen_password() -> str:
    password = ''
    pw_str = string.digits+string.ascii_uppercase
    for ch in ['I', 'O', '0', 'J', 'Z', 'C']:
        pw_str = pw_str.replace(ch, '')
    length = len(pw_str)
    for i in range(5):
        password += pw_str[random.randint(0, length-1)]
    await sleep(0.01)

    return password


@logger.catch
async def update_password() -> str:
    pw = await gen_password()
    pw_dict = {'employee_password': pw}
    await set_json('data.json', pw_dict)

    return pw


@logger.catch
async def generate_id() -> str:
    hash_data = ''
    for i in range(10):
        hash_data += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)]
    await sleep(0.01)

    return hashlib.md5(hash_data.encode()).hexdigest()


@logger.catch
async def generate_order_number() -> int:
    low = 10**6
    high = 10**7 - 1
    order_number = random.randint(low, high)

    while await OrderDB.get_order_numbers(order_number):
        order_number += 1
        if order_number > high:
            order_number = random.randint(low, high)

    return order_number


@logger.catch
async def get_time():
    now = datetime.datetime.now() + datetime.timedelta(hours=TIME_ZONE)
    time = now.strftime('%H:%M')
    hour = now.hour
    minute = now.minute
    await sleep(0.01)

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
async def error_to_db(message: types.Message, bot):
    now = datetime.datetime.now() + datetime.timedelta(hours=TIME_ZONE)
    date = now.strftime('%d.%m.%Y')
    time = await get_time()
    await OrderDB.insert_error(message.from_user.full_name, message.text, date, time[0])

    await bot.send_message(
        chat_id=message.from_user.id,
        text=ERROR_F
    )

    await bot.send_message(
        chat_id=5765637028,
        text=message.from_user.full_name + '\n' + message.text
    )
