
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from order_db import OrderDB
from main import menu
from functions import get_json

TIME_ZONE = 5


async def basket_menu_page(user_id) -> InlineKeyboardMarkup:
    prices = await OrderDB.get_prices()
    order = await OrderDB.get_order_list(user_id)
    ikb = InlineKeyboardMarkup(row_width=3)
    total_price = 0
    try:
        for item in order:
            for price in prices:
                if item == price[0]:
                    p = order[item] * price[1]
                    total_price += p
            ikb.row(InlineKeyboardButton(f'➖       {item}', callback_data=f'!dn_{item}'),
                    InlineKeyboardButton(f'[{order[item]}шт.]          ➕', callback_data=f'!up_{item}'))
    except TypeError:
        return menu

    ikb.add(InlineKeyboardButton('Указать время', callback_data='set_time'))
    ikb.insert(InlineKeyboardButton('Комментарий', callback_data='order_comment'))
    ikb.add(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))
    ikb.add(InlineKeyboardButton(f'Оплатить {total_price},00 RUB', callback_data='pay'))

    return ikb


async def product_page(user_id, product) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=3)
    ikb.row(InlineKeyboardButton('-', callback_data=f'-{product}'),
            InlineKeyboardButton(f'{await OrderDB.get_count(user_id)}', callback_data='None'),
            InlineKeyboardButton('+', callback_data=f'+{product}'))
    ikb.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'basket_add_{product}'))
    products_count = await OrderDB.get_products_count(user_id)
    if products_count == 0:
        ikb.add(InlineKeyboardButton('Корзина', callback_data='basket'))
    else:
        ikb.add(InlineKeyboardButton(f'Корзина ({products_count})', callback_data='basket'))
    ikb.insert(InlineKeyboardButton('Меню', switch_inline_query_current_chat='#menu'))

    return ikb


async def employees_page() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=3)
    employees_list = await OrderDB.get_id_name_by_status('Повар')
    for employee in employees_list:
        ikb.add(InlineKeyboardButton('🚫', callback_data=f'remove_employee_{employee[0]}'))
        ikb.insert(InlineKeyboardButton(f'{employee[1]}', callback_data='None'))

    ikb.add(InlineKeyboardButton('Сменить пароль', callback_data='change_password'))
    ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
    ikb.insert(InlineKeyboardButton('Помощь', callback_data='employee_help'))

    return ikb


async def edit_menu_page(del_product: bool, page=1) -> InlineKeyboardMarkup:
    rows = 6
    ikb = InlineKeyboardMarkup(row_width=3)
    prices_list = await OrderDB.get_prices()
    prices_list_rows = prices_list[rows*page-rows:rows*page]
    next_page_len = len(prices_list) - rows*page

    for product, price, desc, url in prices_list_rows:
        if del_product:
            ikb.add(InlineKeyboardButton('🚫', callback_data='remove_product_' + product))
            ikb.insert(InlineKeyboardButton(product, callback_data='None'))
        else:
            ikb.add(InlineKeyboardButton('✏ ', callback_data='change_desc_'+product))
            ikb.insert(InlineKeyboardButton('🌆'+product, callback_data=f'change_image_{product}'))
            ikb.insert(InlineKeyboardButton(f'{price}₽', callback_data='change_price_'+product))

    ikb.add(InlineKeyboardButton('◀️', callback_data=f'prev_menu_page {page} {next_page_len} {del_product}'))
    ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))
    ikb.insert(InlineKeyboardButton('▶️', callback_data=f'next_menu_page {page} {next_page_len} {del_product}'))

    if del_product:
        ikb.add(InlineKeyboardButton('Назад', callback_data='back_to_edit_menu'))
    else:
        ikb.add(InlineKeyboardButton('Удалить товар', callback_data='menu_delete'))
        ikb.insert(InlineKeyboardButton('Добавить товар', callback_data='menu_add'))
        ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
        ikb.insert(InlineKeyboardButton('Помощь', callback_data='menu_help'))

    return ikb


async def settings_page() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    state = get_json('data.json')['is_bot_enabled']
    if state:
        ikb.add(InlineKeyboardButton('Выключить бота', callback_data='state_bot_off'))
    else:
        ikb.add(InlineKeyboardButton('Включить бота', callback_data='state_bot_on'))
    ikb.add(InlineKeyboardButton('Стартовое изображение', callback_data='change_main_image'))
    ikb.add(InlineKeyboardButton('Назад', callback_data='back'))

    return ikb


async def mails_page() -> InlineKeyboardMarkup:
    mails_count = await OrderDB.get_mails_count()
    mails = f'Мои рассылки ({mails_count})' if mails_count else 'Мои рассылки'
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton('Создать рассылку', callback_data='create_mail'))
    ikb.add(InlineKeyboardButton(mails, callback_data='my_mails'))
    ikb.add(InlineKeyboardButton('Назад', callback_data='back'))
    ikb.insert(InlineKeyboardButton('Помощь', callback_data='mails_help'))

    return ikb


async def my_mails(page: int) -> InlineKeyboardMarkup:
    pages = await OrderDB.get_mails_count()

    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton('◀️', callback_data=f'prev_my_mails {page} {pages}'))
    ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))
    ikb.insert(InlineKeyboardButton('▶️', callback_data=f'next_my_mails {page} {pages}'))
    ikb.add(InlineKeyboardButton('Удалить', callback_data='delete_mail'))
    ikb.add(InlineKeyboardButton('Назад', callback_data='admin_mails'))
    ikb.insert(InlineKeyboardButton('Отправить', callback_data='send_mail'))

    return ikb


async def set_time_page(user_id: int, hour: int, minute: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=6)
    if hour > 23:
        hour -= 24

    if 0 <= minute < 15:
        minute = 15
    elif 15 <= minute < 30:
        minute = 30
    elif 30 <= minute < 45:
        minute = 45
    elif 45 <= minute < 60:
        minute = 0

    hour_var = 0
    minute_var = 0

    for i in range(24):
        if hour+hour_var < 10:
            h = f'0{hour+hour_var}'
        else:
            h = hour+hour_var
        if minute+minute_var == 0:
            m = '00'
        else:
            m = minute+minute_var

        if hour+hour_var == 24:
            h = '00'

        ikb.insert(InlineKeyboardButton(f'{h}:{m}',
                                        callback_data=f'set_time_{h}:{m}'))
        if hour+hour_var > 23:
            hour = 0
            hour_var = 0

        minute_var += 15
        if minute+minute_var > 45:
            minute = 0
            minute_var = 0
            hour_var += 1

    ikb.add(InlineKeyboardButton('◀️', callback_data='prev_time_page'))
    ikb.insert(InlineKeyboardButton('▶️', callback_data='next_time_page'))
    order_user_time = await OrderDB.get_order_user_time(user_id)
    if order_user_time is not None:
        ikb.add(InlineKeyboardButton(f'[{order_user_time}] Отменить', callback_data='cancel_set_time'))
    ikb.add(InlineKeyboardButton('Назад', callback_data='back_to_basket'))

    return ikb


async def comment_page() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton('Назад', callback_data='back_to_basket'))
    ikb.insert(InlineKeyboardButton('Удалить', callback_data='del_back_to_basket'))

    return ikb


async def my_orders_navigation(page: int, pages: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton('◀️', callback_data=f'prev_my_orders {page} {pages}'))
    ikb.insert(InlineKeyboardButton(f'{page}', callback_data='None'))
    ikb.insert(InlineKeyboardButton('▶️', callback_data=f'next_my_orders {page} {pages}'))

    return ikb
