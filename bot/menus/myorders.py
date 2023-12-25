from aiogram import Bot
from aiogram.types import CallbackQuery

from bot.menus.menu import Menu
from bot.functions import *
from bot.markups import *


class MyOrders(Menu):

    @staticmethod
    async def get_page(
            count: int, selected_page: int, user_orders_count: int, user_orders: list
    ) -> str:

        num = 1
        answer = ''
        rows = 5

        if selected_page == 0:
            or_num = [_ for _ in range(1, user_orders_count + 1)][count * -1:]
            for order_number, price, order_list, date, time in user_orders[count * -1:]:
                answer += f'[{or_num[num - 1]}]  <b>Заказ №<u>{order_number}</u></b>\n' \
                          f'{order_list} | <b>Оплата: {price}₽</b>\n[{date} {time}]\n\n'
                num += 1
        else:
            end = selected_page * rows
            start = end - rows
            or_num = [_ for _ in range(1, user_orders_count + 1)][start:end]
            for order_number, price, order_list, date, time in user_orders[start:end]:
                answer += f'[{or_num[num - 1]}]  <b>Заказ №<u>{order_number}</u></b>\n' \
                          f'{order_list} | <b>Оплата: {price}₽</b>\n[{date} {time}]\n\n'
                num += 1

        await sleep(0.01)

        return answer

    async def show_page(
            self, message, bot: Bot, user_id: int, msg_id: int, selected_page: int = 0
    ):
        user_orders = await self.db.get_user_orders(message.from_user.id)
        user_orders_count = len(user_orders)

        if user_orders_count != 0:
            if user_orders_count > 5:
                last_page = user_orders_count % 5
                order_pages = user_orders_count // 5
                page = 0 if last_page == 0 else 1
                total_pages = int(order_pages) + page
                if last_page == 0:
                    last_page = 5

                if selected_page == 0:
                    await message.answer(
                        text=await self.get_page(
                            last_page, selected_page, user_orders_count, user_orders
                        ),
                        reply_markup=await self.get_markup(total_pages, total_pages)
                    )
                else:
                    await bot.edit_message_text(
                        text=await self.get_page(
                            last_page, selected_page, user_orders_count, user_orders
                        ),
                        chat_id=user_id,
                        message_id=msg_id,
                        reply_markup=await self.get_markup(selected_page, total_pages)
                    )
            else:
                if selected_page == 0:
                    await message.answer(self.get_page(
                        user_orders_count, selected_page, user_orders_count, user_orders
                    )
                    )
                else:
                    await bot.send_message(
                        chat_id=user_id,
                        text=self.get_page(
                            user_orders_count, selected_page, user_orders_count, user_orders
                        )
                    )
        else:
            await bot.send_message(
                chat_id=user_id,
                text='Список заказов пуст'
            )

    @staticmethod
    async def get_markup(page: int, pages: int) -> InlineKeyboardMarkup:
        ikb = InlineKeyboardMarkup()
        ikb.add(InlineKeyboardButton('◀️', callback_data=f'prev_my_orders {page} {pages}'))
        ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))
        ikb.insert(InlineKeyboardButton('▶️', callback_data=f'next_my_orders {page} {pages}'))

        return ikb

    async def pagination(self, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        data = callback.data.split()
        page = int(data[1])
        if 'prev' in callback.data:
            if page != 1:
                await self.show_page(callback, bot, user_id, msg_id, page - 1)
        else:
            total_pages = int(data[2])
            if page != total_pages:
                await self.show_page(callback, bot, user_id, msg_id, page + 1)


my_orders = MyOrders()
