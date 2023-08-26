from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ikb = InlineKeyboardMarkup()
ikb.add(InlineKeyboardButton('Оформить заказ', switch_inline_query_current_chat='#menu'))


menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))

basket = InlineKeyboardMarkup()
basket.add(InlineKeyboardButton('Корзина', callback_data='basket_edit'))

ikb_cancel = InlineKeyboardMarkup()
ikb_cancel.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

ikb_admin = InlineKeyboardMarkup()
ikb_admin.row(InlineKeyboardButton('Персонал', callback_data='admin_s'),
              InlineKeyboardButton('Редактор меню', callback_data='admin_m'))
ikb_admin.add(InlineKeyboardButton('Статистика', callback_data='admin_stats'))
ikb_admin.add(InlineKeyboardButton('Настройки', callback_data='settings'))

ikb_back = InlineKeyboardMarkup()
ikb_back.add(InlineKeyboardButton('Назад', callback_data='back'))

ikb_add_image = InlineKeyboardMarkup()
ikb_add_image.add(InlineKeyboardButton('Без изображения', callback_data='without_image'))
ikb_add_image.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

ikb_settings = InlineKeyboardMarkup()
ikb_settings.add(InlineKeyboardButton('Стартовое изображение', callback_data='change_main_image'))
ikb_settings.add(InlineKeyboardButton('Назад', callback_data='back'))

ikb_employees = InlineKeyboardMarkup()
ikb_employees.add(InlineKeyboardButton('Заказы за 24 часа', callback_data='24h_orders'))