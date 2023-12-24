from aiogram import Bot
from aiogram.types import CallbackQuery

from bot.menus.menu import Menu
from bot.functions import *
from bot.messages import *
from bot.markups import *


class Employees(Menu):

    @classmethod
    async def get_page(cls) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup(row_width=3)
        employees_list = await cls.db.get_id_name_by_status('Повар')
        for employee in employees_list:
            ikb.add(InlineKeyboardButton('🚫', callback_data=f'delete_employee_{employee[0]}'))
            ikb.insert(InlineKeyboardButton(f'{employee[1]}', callback_data='None'))

        ikb.add(InlineKeyboardButton('Сменить пароль', callback_data='update_password'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
        ikb.insert(InlineKeyboardButton('Помощь', callback_data='employee_help'))

        return ikb

    @classmethod
    async def show_page(cls, user_id: int, msg_id: int, bot: Bot,
                        update_pw: bool = False, show_help: bool = False):
        if update_pw:
            pw = await update_password()
        else:
            password = await get_json()
            pw = password["employee_password"]

        help_msg = EMPLOYEE_HELP if show_help else ''

        await bot.edit_message_text(
            text=EMPLOYEE_TITLE + f'\nПароль для персонала: <b>{pw}</b>{help_msg}',
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await cls.get_page()
        )

    @classmethod
    async def delete(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        employee_id = int(callback.data[16:])
        await cls.db.delete_employee(employee_id)
        await cls.show_page(user_id, msg_id, bot)

    @classmethod
    async def send_order_to_employees(
            cls, comment: str, order_list: str, bot: Bot, order_number: int, user_time_str: str,
            price: int, date: str, time: str
    ):

        if comment is None:
            comm = ''
        else:
            comm = f'\n\n✏ Комментарий: {comment}'

        order = json.loads(order_list.replace('\'', '"'))
        order_str = ''
        for employee in await cls.db.get_id_by_status('Повар'):
            for product in order:
                order_str += f'\n ▫️ {product}: {order[product]}'

            await bot.send_message(
                chat_id=employee,
                text=f'<b>Заказ №<u>{order_number}</u></b>' + user_time_str + order_str +
                     f'\n__________\n'
                     f'{price}₽' + comm + f'\n\n'
                     f'{date} {time}'
            )
