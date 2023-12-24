import aiogram.utils.exceptions
from aiogram import Bot
from aiogram.types import CallbackQuery, LabeledPrice

from bot.menus.menu import Menu
from bot.config import PAY_TOKEN
from bot.functions import *
from bot.messages import *
from bot.markups import *
from bot.states import *


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

        if order:
            ikb.add(InlineKeyboardButton(f'Оплатить {total_price},00 RUB', callback_data='pay'))

        return ikb

    @classmethod
    async def show_page(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot,
                        check_basket: bool = False):
        if check_basket:
            if await cls.db.get_order_list(user_id) is None:
                await callback.answer('Корзина пуста')
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=await cls.get_title(user_id),
                    reply_markup=await cls.get_page(user_id)
                )
        else:
            if 'del' in callback.data:
                await cls.db.delete_comment(user_id)
                await callback.answer('Комментарий удалён')

            await bot.edit_message_text(
                text=await cls.get_title(user_id),
                chat_id=user_id,
                message_id=msg_id,
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
            await cls.show_page(user_id, msg_id, callback, bot)

            await callback.answer('Точное время отменено')
        else:
            time = callback.data[9:]
            await callback.answer(time)
            await cls.db.set_order_user_time(user_id, time)
            await cls.show_page(user_id, msg_id, callback, bot)

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
                reply_markup=await cls.get_markup()
            )

    @staticmethod
    async def get_markup() -> InlineKeyboardMarkup:
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
        await cls.db.add_order(user_id, {product: count})

        if await cls.db.get_temp_products_count(user_id) == 0:
            await cls.db.clear_basket(user_id)

            await bot.edit_message_text(
                text=EMPTY_BASKET,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.get_page(user_id)
            )

            return

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await cls.get_page(user_id)
        )

    @classmethod
    async def get_pay_invoice(cls, user_id: int, bot: Bot):
        order_prices = []
        order_list = await cls.db.get_order_list(user_id)
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
