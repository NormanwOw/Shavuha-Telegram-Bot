from aiogram import Bot
from aiogram.types import CallbackQuery

from bot.menus.menu import Menu
from bot.messages import *
from bot.markups import *
from bot.states import *
from tasks.tasks import get_xlsx


class Admin(Menu):

    @staticmethod
    async def get_page() -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup()
        ikb.row(InlineKeyboardButton('Персонал', callback_data='admin_employees'),
                InlineKeyboardButton('Редактор меню', callback_data='admin_menu'))
        ikb.row(InlineKeyboardButton('Статистика', callback_data='admin_stats'),
                InlineKeyboardButton('Рассылки', callback_data='admin_mails'))
        ikb.add(InlineKeyboardButton('История заказов .xlsx', callback_data='admin_xlsx'))
        ikb.add(InlineKeyboardButton('Сообщить об ошибке', callback_data='admin_error'))
        ikb.add(InlineKeyboardButton('Настройки', callback_data='admin_settings'))

        return ikb

    async def show_page(self, user_id: int, msg_id: int, bot: Bot, show_stats: bool = False):
        if show_stats:
            avg_price = await self.db.get_avg_order_price()
            orders_day = await self.db.get_orders_count_days(1)
            orders_month = await self.db.get_orders_count_days(30)
            orders = await self.db.get_orders_count()
            stats = f'\n ▫️ Заказов за 24 часа: {orders_day}' \
                    f'\n ▫️ Заказов за 30 дней: {orders_month}' \
                    f'\n ▫️ Всего заказов: {orders}' \
                    f'\n ▫️ Средний чек: {int(avg_price)}'
        else:
            stats = ''

        await bot.edit_message_text(
            text=ADMIN_TITLE + stats,
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await self.get_page()
        )

    @staticmethod
    async def get_xlsx(user_id: int):
        get_xlsx.delay(user_id)

    @staticmethod
    async def get_error(callback: CallbackQuery):
        await callback.message.answer(
            text=ERROR_TITLE,
            reply_markup=ikb_cancel
        )
        await ErrorHandler.get_error.set()


admin = Admin()
