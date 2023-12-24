import aiogram.utils.exceptions
from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from bot.menus.menu import Menu
from bot.functions import *
from bot.messages import *
from bot.markups import *
from bot.states import *


class EditMenu(Menu):

    product_list = []

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
                ikb.add(InlineKeyboardButton('🚫', callback_data='delete_product_' + product))
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
            ikb.add(InlineKeyboardButton('Удалить товар', callback_data='del_product_page'))
            ikb.insert(InlineKeyboardButton('Добавить товар', callback_data='add_product_page'))
            ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
            ikb.insert(InlineKeyboardButton('Помощь', callback_data='menu_help'))

        return ikb

    @classmethod
    async def show_page(
            cls, user_id: int, msg_id: int, bot: Bot, show_help: bool = False,
            del_product: bool = False, page: int = 1
    ):
        msg_help = MENU_HELP if show_help else ''

        await bot.edit_message_text(
            text=EDIT_MENU_TITLE + msg_help,
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await cls.get_page(del_product, page)
        )

    @classmethod
    async def change_desc(cls, user_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[12:]
        await ChangeProduct.set_product(product)
        await ChangeProduct.get_new_desc.set()

        await bot.send_message(
            chat_id=user_id,
            text='Введите описание товара (состав):',
            reply_markup=ikb_cancel
        )

        await callback.answer('Редактирование описания')

    @classmethod
    async def change_image(cls, user_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[13:]
        await ChangeProduct.set_product(product)
        await ChangeProduct.get_new_product_image.set()

        await bot.send_message(
            chat_id=user_id,
            text='Отправьте ссылку на изображение:',
            reply_markup=ikb_cancel
        )

        await callback.answer('Редактирование изображения')

    @classmethod
    async def change_price(cls, user_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[13:]
        await ChangeProduct.set_product(product)
        await ChangeProduct.get_new_price.set()

        await bot.send_message(
            chat_id=user_id,
            text='Введите стоимость товара:',
            reply_markup=ikb_cancel
        )

        await callback.answer('Редактирование цены')

    @classmethod
    async def add_product(cls, user_id: int, callback: CallbackQuery, bot: Bot):
        await bot.send_message(
            chat_id=user_id,
            text='Введите название товара:',
            reply_markup=ikb_cancel
        )

        await AddProduct.get_name.set()
        await callback.answer('Добавление товара')

    @classmethod
    async def delete_product(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        product = callback.data[15:]
        await cls.db.delete_product(product)
        await cls.show_page(user_id, msg_id, bot)
        await callback.answer(f'Товар удалён', show_alert=True)

    @classmethod
    async def pagination(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        del_product = True if 'True' in callback.data else False
        data = callback.data.split()
        page = int(data[1])
        next_page_len = int(data[2])

        if 'next' in callback.data and next_page_len > 0:
            await cls.show_page(user_id, msg_id, bot, del_product=del_product, page=page + 1)

        elif 'prev' in callback.data and page != 1:
            await cls.show_page(user_id, msg_id, bot, del_product=del_product, page=page - 1)

    @classmethod
    async def add_image(cls, message: types.Message, bot: Bot, state: FSMContext):
        try:
            await bot.send_photo(message.from_user.id, message.text)

            await bot.send_message(
                message.from_user.id,
                '✅ Товар добавлен\n\n' + EDIT_MENU_TITLE,
                reply_markup=await cls.get_page(False)
            )

            cls.product_list.append(message.text)
            await OrderDB.add_product(cls.product_list)
            cls.product_list.clear()
            await state.finish()
        except aiogram.utils.exceptions.BadRequest:

            await bot.send_message(
                message.from_user.id,
                'Неверная ссылка, изображение не найдено',
                reply_markup=ikb_cancel
            )

        await message.delete()

    @classmethod
    async def add_desc(cls, message: types.Message, bot: Bot):
        cls.product_list.append(message.text)

        await bot.send_message(
            message.from_user.id,
            'Отправьте изображение:',
            reply_markup=ikb_add_image
        )

        await AddProduct.get_image.set()
        await message.delete()

    @classmethod
    async def add_price(cls, message: types.Message, bot: Bot):
        try:
            if int(message.text) >= 0:
                await bot.send_message(
                    message.from_user.id,
                    'Введите состав:',
                    reply_markup=ikb_cancel
                )

                cls.product_list.append(int(message.text))
                await AddProduct.get_desc.set()
        except ValueError:
            pass
        await message.delete()

    @classmethod
    async def add_name(cls, message: types.Message, bot: Bot):
        if len(message.text) > 1:
            await bot.send_message(
                message.from_user.id,
                'Введите стоимость товара:',
                reply_markup=ikb_cancel
            )

            cls.product_list.append(message.text)
            await AddProduct.get_price.set()
        await message.delete()

    @classmethod
    async def get_product_list(cls):
        return cls.product_list
