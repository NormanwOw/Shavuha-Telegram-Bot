import aiogram.utils.exceptions
from aiogram import Bot
from aiogram.types import CallbackQuery

from bot.menus.menu import Menu
from bot.functions import *
from bot.markups import *


class Products(Menu):

    async def get_page(self, user_id: int, product: str) -> InlineKeyboardMarkup:
        count = await self.db.get_count_by_product(user_id, product)
        ikb = InlineKeyboardMarkup(row_width=3)
        ikb.row(InlineKeyboardButton('-', callback_data=f'-{product}'),
                InlineKeyboardButton(f'{count}', callback_data='None'),
                InlineKeyboardButton('+', callback_data=f'+{product}'))
        ikb.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'basket_add_{product}'))

        products_count = await self.db.get_basket_products_count(user_id)
        if products_count == 0:
            ikb.add(InlineKeyboardButton('Корзина', callback_data='basket'))
        else:
            ikb.add(InlineKeyboardButton(f'Корзина ({products_count})', callback_data='basket'))
        ikb.insert(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))

        return ikb

    async def show_page(self, message: types.Message, bot: Bot):
        product_list = await self.db.get_prices()
        for product in product_list:
            if message.text == product[0]:
                try:
                    await bot.send_photo(
                        message.from_user.id,
                        photo=product[3],
                        caption=f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                        reply_markup=await self.get_page(message.from_user.id, product[0])
                    )

                except aiogram.utils.exceptions.BadRequest:

                    await bot.send_message(
                        message.from_user.id,
                        f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                        reply_markup=await self.get_page(message.from_user.id, product[0])
                    )
                await self.db.delete_temp(message.from_user.id)
                await self.db.update_temp(message.from_user.id, product[0], 1)
        await message.delete()

    async def product_counter(self, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[1:]
        count = 0

        if '+' in callback.data:
            count = await self.db.update_temp(user_id, product, 1)
        elif '-' in callback.data:
            count = await self.db.update_temp(user_id, product, -1)

        if count > 0:
            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await self.get_page(user_id, product)
            )

    async def add(self, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[11:]
        time = await get_time()
        await self.db.from_temp_to_basket(user_id)
        await self.db.set_order_time(user_id, time[0])
        await callback.answer('Товар добавлен в корзину')

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await self.get_page(user_id, product)
        )


products = Products()
