import aiogram.utils.exceptions
from aiogram import Bot
from aiogram.types import CallbackQuery

from bot.menus.menu import Menu
from bot.functions import *
from bot.markups import *


class Product(Menu):

    @classmethod
    async def get_page(cls, user_id: int, product: str) -> InlineKeyboardMarkup:
        count = await cls.db.get_count_by_product(user_id, product)
        ikb = InlineKeyboardMarkup(row_width=3)
        ikb.row(InlineKeyboardButton('-', callback_data=f'-{product}'),
                InlineKeyboardButton(f'{count}', callback_data='None'),
                InlineKeyboardButton('+', callback_data=f'+{product}'))
        ikb.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'basket_add_{product}'))

        products_count = await cls.db.get_basket_products_count(user_id)
        if products_count == 0:
            ikb.add(InlineKeyboardButton('Корзина', callback_data='basket'))
        else:
            ikb.add(InlineKeyboardButton(f'Корзина ({products_count})', callback_data='basket'))
        ikb.insert(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))

        return ikb

    @classmethod
    async def show_page(cls, message: types.Message, bot: Bot):
        print('asd')
        products = await cls.db.get_prices()
        for product in products:
            if message.text == product[0]:
                try:
                    await bot.send_photo(
                        message.from_user.id,
                        photo=product[3],
                        caption=f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                        reply_markup=await cls.get_page(message.from_user.id, product[0])
                    )

                except aiogram.utils.exceptions.BadRequest:

                    await bot.send_message(
                        message.from_user.id,
                        f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                        reply_markup=await cls.get_page(message.from_user.id, product[0])
                    )
                await cls.db.delete_temp(message.from_user.id)
                await cls.db.update_temp(message.from_user.id, product[0], 1)
        await message.delete()

    @classmethod
    async def product_counter(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[1:]
        count = 0

        if '+' in callback.data:
            count = await cls.db.update_temp(user_id, product, 1)
        elif '-' in callback.data:
            count = await cls.db.update_temp(user_id, product, -1)

        if count > 0:
            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.get_page(user_id, product)
            )

    @classmethod
    async def add(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[11:]
        time = await get_time()
        await cls.db.from_temp_to_basket(user_id)
        await cls.db.set_order_time(user_id, time[0])
        await callback.answer('Товар добавлен в корзину')

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await cls.get_page(user_id, product)
        )
