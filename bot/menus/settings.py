from aiogram import Bot
from aiogram.types import CallbackQuery

from bot.menus.menu import Menu
from bot.functions import *
from bot.messages import *
from bot.markups import *
from bot.states import *


class Settings(Menu):

    @staticmethod
    async def get_page() -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup()
        data = await get_json()
        bot_enabled = data['is_bot_enabled']

        if bot_enabled:
            ikb.add(InlineKeyboardButton('Выключить бота', callback_data='state_bot_off'))
        else:
            ikb.add(InlineKeyboardButton('Включить бота', callback_data='state_bot_on'))

        ikb.add(InlineKeyboardButton('Стартовое изображение', callback_data='change_main_image'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='back'))

        return ikb

    async def show_page(self, user_id: int, msg_id: int, bot: Bot):
        await bot.edit_message_text(
            text=SETTINGS_TITLE,
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await self.get_page()
        )

    async def switch_state(self, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        if 'off' in callback.data:
            await set_json({'is_bot_enabled': 0})
            await callback.answer('Приём заказов остановлен', show_alert=True)
        else:
            await set_json({'is_bot_enabled': 1})
            await callback.answer('Приём заказов запущен', show_alert=True)

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await self.get_page()
        )

    @staticmethod
    async def change_main_image(user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        await bot.edit_message_text(
            text='Отправьте изображение:',
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=ikb_cancel
        )
        await ChangeMainImage.get_main_image.set()
        await callback.answer('Редактирование изображения')


settings = Settings()
