from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton

ikb_main = InlineKeyboardMarkup()
ikb_main.add(InlineKeyboardButton('Оформить заказ', switch_inline_query_current_chat='#menu'))

menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))

basket = InlineKeyboardMarkup()
basket.add(InlineKeyboardButton('Корзина', callback_data='basket_edit'))

ikb_cancel = InlineKeyboardMarkup()
ikb_cancel.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

rkb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
rkb_admin.add(KeyboardButton('Панель управления'))

ikb_back = InlineKeyboardMarkup()
ikb_back.add(InlineKeyboardButton('Назад', callback_data='back'))

ikb_add_image = InlineKeyboardMarkup()
ikb_add_image.add(InlineKeyboardButton('Без изображения', callback_data='without_image'))
ikb_add_image.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

rkb_employee = ReplyKeyboardMarkup(resize_keyboard=True)
rkb_employee.add(KeyboardButton('Список заказов за 24 часа'))

ikb_send_mail = InlineKeyboardMarkup()
ikb_send_mail.row(InlineKeyboardButton('Нет', callback_data='send_mail_no'),
                  InlineKeyboardButton('Да', callback_data='send_mail_yes'))

ikb_del_mail = InlineKeyboardMarkup()
ikb_del_mail.row(InlineKeyboardButton('Нет', callback_data='delete_mail_no'),
                 InlineKeyboardButton('Да', callback_data='delete_mail_yes'))
