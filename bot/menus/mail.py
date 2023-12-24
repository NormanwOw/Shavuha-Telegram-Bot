from aiogram import Bot
from aiogram.types import CallbackQuery

from bot.menus.menu import Menu
from bot.messages import *
from bot.markups import *
from bot.states import *
from tasks.tasks import send_mail


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
    async def show_page(cls, user_id: int, msg_id: int, bot: Bot, show_help: bool = False):
        help_msg = MAILS_HELP if show_help else ''

        await bot.edit_message_text(
            text=MAILS_TITLE + help_msg,
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=await cls.get_page()
        )

    @classmethod
    async def my_mails(cls, page: int) -> InlineKeyboardMarkup:
        pages = await cls.db.get_mails_count()

        ikb = InlineKeyboardMarkup()
        ikb.add(InlineKeyboardButton('◀️', callback_data=f'prev_my_mails {page} {pages}'))
        ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))
        ikb.insert(InlineKeyboardButton('▶️', callback_data=f'next_my_mails {page} {pages}'))
        ikb.add(InlineKeyboardButton('Удалить', callback_data='delete_mail'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='admin_mails'))
        ikb.insert(InlineKeyboardButton('Отправить', callback_data='send_mail'))

        return ikb

    @classmethod
    async def get_mails(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        data = callback.data.split()

        if 'prev' in callback.data:
            page = int(data[1])
            if page == 1:
                return await callback.answer()
            await cls.db.move_selected_mail(False)
            page -= 1
        elif 'next' in callback.data:
            page = int(data[1])
            total_pages = int(data[2])
            if page == total_pages:
                return await callback.answer()
            await cls.db.move_selected_mail(True)
            page += 1
        try:
            mail_id, mail_text = await cls.db.get_mail()
            await bot.edit_message_text(
                text=mail_text,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await cls.my_mails(mail_id)
            )
        except TypeError:
            await callback.answer('Список рассылок пуст')

    @classmethod
    async def create(cls, user_id: int, bot: Bot):
        await StateMail.new_mail.set()
        await bot.send_message(
            chat_id=user_id,
            text='Введите текст рассылки',
            reply_markup=ikb_cancel
        )

    @classmethod
    async def delete(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        if 'yes' in callback.data:
            state = await cls.db.delete_mail()
            await callback.answer('Рассылка удалена', show_alert=True)
            if state:
                mail_id, mail_text = await cls.db.get_mail()

                await bot.edit_message_text(
                    text=mail_text,
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await cls.my_mails(mail_id)
                )
            else:
                await cls.show_page(user_id, msg_id, bot)

        elif 'no' in callback.data:
            await callback.answer('Удаление отменено', show_alert=True)
            await bot.delete_message(user_id, msg_id)
        else:
            await bot.send_message(
                chat_id=user_id,
                text='Удалить рассылку?',
                reply_markup=ikb_del_mail
            )

    @classmethod
    async def send(cls, user_id: int, msg_id: int, callback: CallbackQuery, bot: Bot):
        if 'yes' in callback.data:
            send_mail.delay(user_id)

        elif 'no' in callback.data:
            await callback.answer('Отправление отменено', show_alert=True)
            await bot.delete_message(user_id, msg_id)
        else:
            mail_text = await cls.db.get_mail()

            await bot.send_message(
                chat_id=user_id,
                text=SEND_MAIL + mail_text[1],
                reply_markup=ikb_send_mail
            )
        await bot.delete_message(user_id, msg_id)
