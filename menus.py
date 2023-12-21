from abc import ABC, abstractmethod

from aiogram.types import CallbackQuery, LabeledPrice
import aiogram.utils.exceptions

from config import PAY_TOKEN
from functions import *
from messages import *
from markups import *
from states import *
from config import logger


class Menu(ABC):
    db = OrderDB

    @classmethod
    @abstractmethod
    async def get_page(cls, *args):
        pass


class Basket(Menu):

    @classmethod
    async def get_page(cls, user_id: int) -> InlineKeyboardMarkup:
        prices = await cls.db.get_prices()
        order = await cls.db.get_order_list(user_id)
        ikb = InlineKeyboardMarkup(row_width=3)
        total_price = 0
        try:
            for item in order:
                for price in prices:
                    if item == price[0]:
                        p = order[item] * price[1]
                        total_price += p
                ikb.row(InlineKeyboardButton(f'➖       {item}',
                                             callback_data=f'!dn_{item}'),
                        InlineKeyboardButton(f'[{order[item]}шт.]          ➕',
                                             callback_data=f'!up_{item}'))
        except TypeError:
            return menu

        ikb.add(InlineKeyboardButton('Указать время', callback_data='set_time'))
        ikb.insert(InlineKeyboardButton('Комментарий', callback_data='order_comment'))
        ikb.add(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))
        ikb.add(InlineKeyboardButton(f'Оплатить {total_price},00 RUB', callback_data='pay'))

        return ikb

    @classmethod
    async def back_to_page(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        if 'del' in callback.data:
            await OrderDB.delete_comment(user_id)
            await callback.answer('Комментарий удалён')

        await bot.edit_message_text(
            text=await Basket.get_title(user_id),
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await Basket.get_page(user_id)
        )

    @classmethod
    async def show_page(cls, user_id: int, callback: CallbackQuery, bot: Bot):
        if await cls.db.get_order_by_id(user_id) is None:
            await callback.answer('Корзина пуста')
        else:
            await bot.send_message(
                chat_id=user_id,
                text=await cls.get_title(user_id),
                reply_markup=await cls.get_page(user_id)
            )

    @classmethod
    async def set_time_page(cls, user_id: int, hour: int, minute: int) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup(row_width=6)
        if hour > 23:
            hour -= 24

        if 0 <= minute < 15:
            minute = 15
        elif 15 <= minute < 30:
            minute = 30
        elif 30 <= minute < 45:
            minute = 45
        elif 45 <= minute < 60:
            minute = 0
            hour += 1

        hour_var = 0
        minute_var = 0

        for i in range(24):
            if hour + hour_var < 10:
                h = f'0{hour + hour_var}'
            else:
                h = hour + hour_var
            if minute + minute_var == 0:
                m = '00'
            else:
                m = minute + minute_var

            if hour + hour_var == 24:
                h = '00'

            ikb.insert(InlineKeyboardButton(
                text=f'{h}:{m}',
                callback_data=f'set_time_{h}:{m}'
                )
            )
            if hour + hour_var > 23:
                hour = 0
                hour_var = 0

            minute_var += 15
            if minute + minute_var > 45:
                minute = 0
                minute_var = 0
                hour_var += 1

        ikb.add(InlineKeyboardButton('◀️', callback_data='prev_time_page'))
        ikb.insert(InlineKeyboardButton('▶️', callback_data='next_time_page'))
        order_user_time = await cls.db.get_order_user_time(user_id)
        if order_user_time is not None:
            ikb.add(InlineKeyboardButton(f'[{order_user_time}] Отменить',
                                         callback_data='cancel_set_time'))
        ikb.add(InlineKeyboardButton('Назад',
                                     callback_data='back_to_basket'))

        return ikb

    @classmethod
    async def show_time_page(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        _, hour, minute = await get_time()
        if 'next' in callback.data:
            hour += 6
        try:
            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.set_time_page(user_id, hour, minute)
            )

        except aiogram.utils.exceptions.MessageNotModified:
            await callback.answer()
            return

    @classmethod
    async def get_title(cls, user_id: int) -> str:
        title = '🛒 <b>Корзина</b>'
        time = await cls.db.get_order_user_time(user_id)
        comment = await cls.db.get_comment(user_id)
        if time is None:
            time = ''
        else:
            time = '\n⏱ ' + await cls.db.get_order_user_time(user_id)

        if comment is None:
            comment = ''
        else:
            comment = '\n✏ ' + comment

        return title + time + comment

    @classmethod
    async def set_time(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        if callback.data == 'set_time':
            time, hour, minute = await get_time()

            await bot.edit_message_text(
                text=SET_TIME_MESSAGE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.set_time_page(user_id, hour, minute)
            )

            await cls.db.set_order_time(user_id, time)

        elif callback.data == 'cancel_set_time':
            if await cls.db.get_order_user_time(user_id) is None:
                await callback.answer()
                return

            await cls.db.set_order_user_time(user_id, None)

            await bot.edit_message_text(
                text=await cls.get_title(user_id),
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.get_page(user_id)
            )

            await callback.answer('Точное время отменено')
        else:
            time = callback.data[9:]
            await callback.answer(time)
            await cls.db.set_order_user_time(user_id, time)

            await bot.edit_message_text(
                text=await cls.get_title(user_id),
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.get_page(user_id)
            )

    @classmethod
    async def get_comment_title(cls, user_id: int) -> str:
        title = '<b>✏ Комментарий к заказу</b>'
        comment = await cls.db.get_comment(user_id)
        if comment is None:
            comment = ''
        else:
            comment = '\n ' + comment
        return title + comment

    @classmethod
    async def set_comment(cls, user_id: int, msg_id: int, bot: Bot):
        if await cls.db.get_comment(user_id) is None:

            await bot.send_message(
                chat_id=user_id,
                text='Комментарий к заказу:',
                reply_markup=ikb_cancel
            )

            await OrderComment.get_comment.set()
        else:
            await bot.edit_message_text(
                text=await cls.get_comment_title(user_id),
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.comment_page()
            )

    @staticmethod
    async def comment_page() -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup()
        ikb.add(InlineKeyboardButton('Назад', callback_data='back_to_basket'))
        ikb.insert(InlineKeyboardButton('Удалить', callback_data='del_back_to_basket'))

        return ikb

    @classmethod
    async def product_counter(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[4:]
        if '!up' in callback.data:
            count = 1
        else:
            count = -1
        await OrderDB.add_order(user_id, {product: count})

        if await OrderDB.get_products_count(user_id) == 0:
            await OrderDB.clear_basket(user_id)

            await bot.edit_message_text(
                text=EMPTY_BASKET,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await Basket.get_page(user_id)
            )

            return

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await Basket.get_page(user_id)
        )

    @classmethod
    async def get_pay_invoice(cls, user_id: int, msg_id: int, bot: Bot):
        data = await cls.db.get_order_by_id(user_id)
        try:
            order_list = json.loads(data[2])
        except TypeError:
            await bot.delete_message(user_id, msg_id)
            return
        order_prices = []

        prices = await cls.db.get_prices()
        desc = ''
        p = ''
        for item in order_list:
            for i in prices:
                if i[0] == item:
                    p = i[1]
            cnt = order_list[item]
            label = item + f' - {cnt}шт.'
            lp = LabeledPrice(label=label, amount=p * cnt * 100)
            order_prices.append(lp)

            desc += f' ▫️ {item}'

        await bot.send_invoice(
            chat_id=user_id,
            title='Заказ',
            description=desc,
            provider_token=PAY_TOKEN,
            currency='rub',
            start_parameter='example',
            payload=order_list,
            prices=order_prices,
            need_shipping_address=False
        )


class Product(Menu):

    @classmethod
    async def get_page(cls, user_id: int, product: str) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup(row_width=3)
        ikb.row(InlineKeyboardButton('-', callback_data=f'-{product}'),
                InlineKeyboardButton(f'{await cls.db.get_count(user_id)}', callback_data='None'),
                InlineKeyboardButton('+', callback_data=f'+{product}'))
        ikb.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'basket_add_{product}'))
        products_count = await cls.db.get_products_count(user_id)
        if products_count == 0:
            ikb.add(InlineKeyboardButton('Корзина', callback_data='basket'))
        else:
            ikb.add(InlineKeyboardButton(f'Корзина ({products_count})', callback_data='basket'))
        ikb.insert(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))

        return ikb

    @classmethod
    async def product_counter(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        count = await cls.db.get_count(user_id)
        product = callback.data[1:]
        if await cls.db.is_temp_exists(user_id) is False:
            await cls.db.add_temp(user_id, product)
        else:
            if '+' in callback.data:
                if count > 21:
                    await callback.answer()
                    return
                await cls.db.set_count(user_id, count + 1)
            else:
                if count == 1:
                    await callback.answer()
                    return
                await cls.db.set_count(user_id, count - 1)

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await cls.get_page(user_id, product)
        )

    @classmethod
    async def add(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[11:]
        time = await get_time()
        await cls.db.temp_to_order(user_id)
        await cls.db.set_order_time(user_id, time[0])
        await callback.answer('Товар добавлен в корзину')

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await cls.get_page(user_id, product)
        )


class Admin(Menu):

    @classmethod
    async def get_page(cls):
        pass


class Employees(Menu):

    @classmethod
    async def get_page(cls) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup(row_width=3)
        employees_list = await cls.db.get_id_name_by_status('Повар')
        for employee in employees_list:
            ikb.add(InlineKeyboardButton('🚫', callback_data=f'remove_employee_{employee[0]}'))
            ikb.insert(InlineKeyboardButton(f'{employee[1]}', callback_data='None'))

        ikb.add(InlineKeyboardButton('Сменить пароль', callback_data='change_password'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
        ikb.insert(InlineKeyboardButton('Помощь', callback_data='employee_help'))

        return ikb


class EditMenu(Menu):

    @classmethod
    async def get_page(cls, del_product: bool, page: int = 1) -> InlineKeyboardMarkup:
        rows = 6
        ikb = InlineKeyboardMarkup(row_width=3)
        prices_list = await cls.db.get_prices()
        prices_list_rows = prices_list[rows * page - rows:rows * page]
        next_page_len = len(prices_list) - rows * page

        if next_page_len < 0:
            next_page_len = 0

        for product, price, desc, url in prices_list_rows:
            if del_product:
                ikb.add(InlineKeyboardButton('🚫', callback_data='remove_product_' + product))
                ikb.insert(InlineKeyboardButton(product, callback_data='None'))
            else:
                ikb.add(InlineKeyboardButton('✏ ', callback_data='change_desc_' + product))
                ikb.insert(
                    InlineKeyboardButton('🌆' + product, callback_data=f'change_image_{product}'))
                ikb.insert(
                    InlineKeyboardButton(f'{price}₽', callback_data='change_price_' + product))

        ikb.add(
            InlineKeyboardButton(
                text='◀️',
                callback_data=f'prev_menu_page {page} {next_page_len} {del_product}'
            )
        )

        ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))

        ikb.insert(
            InlineKeyboardButton(
                text='▶️',
                callback_data=f'next_menu_page {page} {next_page_len} {del_product}'
            )
        )

        if del_product:
            ikb.add(InlineKeyboardButton('Назад', callback_data='back_to_edit_menu'))
        else:
            ikb.add(InlineKeyboardButton('Удалить товар', callback_data='menu_delete'))
            ikb.insert(InlineKeyboardButton('Добавить товар', callback_data='menu_add'))
            ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
            ikb.insert(InlineKeyboardButton('Помощь', callback_data='menu_help'))

        return ikb


class Settings(Menu):

    @staticmethod
    async def get_page() -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup()
        data = await get_json('data.json')
        bot_enabled = data['is_bot_enabled']

        if bot_enabled:
            ikb.add(InlineKeyboardButton('Выключить бота', callback_data='state_bot_off'))
        else:
            ikb.add(InlineKeyboardButton('Включить бота', callback_data='state_bot_on'))

        ikb.add(InlineKeyboardButton('Стартовое изображение', callback_data='change_main_image'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='back'))

        return ikb


class Mail(Menu):

    @classmethod
    async def get_page(cls) -> InlineKeyboardMarkup:
        mails_count = await cls.db.get_mails_count()
        mails = f'Мои рассылки ({mails_count})' if mails_count else 'Мои рассылки'
        ikb = InlineKeyboardMarkup()
        ikb.add(InlineKeyboardButton('Создать рассылку', callback_data='create_mail'))
        ikb.add(InlineKeyboardButton(mails, callback_data='my_mails'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
        ikb.insert(InlineKeyboardButton('Помощь', callback_data='mails_help'))

        return ikb

    @classmethod
    async def my_mails(cls, page: int) -> InlineKeyboardMarkup:
        pages = cls.db.get_mails_count()

        ikb = InlineKeyboardMarkup()
        ikb.add(InlineKeyboardButton('◀️', callback_data=f'prev_my_mails {page} {pages}'))
        ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))
        ikb.insert(InlineKeyboardButton('▶️', callback_data=f'next_my_mails {page} {pages}'))
        ikb.add(InlineKeyboardButton('Удалить', callback_data='delete_mail'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='admin_mails'))
        ikb.insert(InlineKeyboardButton('Отправить', callback_data='send_mail'))

        return ikb


class MyOrders(Menu):

    @staticmethod
    async def get_page(page: int, pages: int) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup()
        ikb.add(InlineKeyboardButton('◀️', callback_data=f'prev_my_orders {page} {pages}'))
        ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))
        ikb.insert(InlineKeyboardButton('▶️', callback_data=f'next_my_orders {page} {pages}'))

        return ikb
