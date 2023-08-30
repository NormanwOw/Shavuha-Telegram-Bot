from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

ikb = InlineKeyboardMarkup()
ikb.add(InlineKeyboardButton('Оформить заказ', switch_inline_query_current_chat='#menu'))


menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))

basket = InlineKeyboardMarkup()
basket.add(InlineKeyboardButton('Корзина', callback_data='basket_edit'))

ikb_cancel = InlineKeyboardMarkup()
ikb_cancel.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

ikb_admin = InlineKeyboardMarkup()
ikb_admin.row(InlineKeyboardButton('Персонал', callback_data='admin_employees'),
              InlineKeyboardButton('Редактор меню', callback_data='admin_menu'))

ikb_admin.row(InlineKeyboardButton('Статистика', callback_data='admin_stats'),
              InlineKeyboardButton('Рассылки', callback_data='admin_sending'))
ikb_admin.add(InlineKeyboardButton('История заказов .xlsx', callback_data='admin_xlsx'))
ikb_admin.add(InlineKeyboardButton('Сообщить об ошибке', callback_data='admin_error'))
ikb_admin.add(InlineKeyboardButton('Настройки', callback_data='admin_settings'))

rkb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
rkb_admin.add(KeyboardButton('Панель управления'))

ikb_back = InlineKeyboardMarkup()
ikb_back.add(InlineKeyboardButton('Назад', callback_data='back'))

ikb_add_image = InlineKeyboardMarkup()
ikb_add_image.add(InlineKeyboardButton('Без изображения', callback_data='without_image'))
ikb_add_image.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

ikb_settings = InlineKeyboardMarkup()
ikb_settings.add(InlineKeyboardButton('Стартовое изображение', callback_data='change_main_image'))
ikb_settings.add(InlineKeyboardButton('Назад', callback_data='back'))

rkb_employee = ReplyKeyboardMarkup(resize_keyboard=True)
rkb_employee.add(KeyboardButton('Список заказов за 24 часа'))
