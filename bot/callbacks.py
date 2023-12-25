import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext
from aiogram import Bot

from database.order_db import database
from bot.messages import *
from bot.functions import *
from bot.menus.admin import admin
from bot.menus.basket import basket
from bot.menus.editmenu import edit_menu
from bot.menus.employees import employees
from bot.menus.mail import mail
from bot.menus.myorders import my_orders
from bot.menus.product import products
from bot.menus.settings import settings


@logger.catch
async def handler(user_id: int, msg_id: int, callback: types.CallbackQuery, bot: Bot):
    try:
        # BASKET PAGE CALLBACKS
        # =========================================================================================

        if callback.data == 'basket':
            await basket.show_page(user_id, msg_id, callback, bot, check_basket=True)

        # SET ORDER TIME PAGE
        if 'set_time' in callback.data:
            await basket.set_time(user_id, msg_id, callback, bot)

        # ORDER COMMENT PAGE
        if callback.data == 'order_comment':
            await basket.set_comment(user_id, msg_id, bot)

        if callback.data == 'pay':
            await basket.get_pay_invoice(user_id, bot)

        # PRODUCT COUNTER AT THE BASKET PAGE
        if '!up' in callback.data or '!dn' in callback.data:
            await basket.product_counter(user_id, msg_id, callback, bot)

        if 'time_page' in callback.data:
            await basket.show_time_page(user_id, msg_id, callback, bot)

        if 'back_to_basket' in callback.data:
            await basket.show_page(user_id, msg_id, callback, bot)

        # ORDER PAGE CALLBACKS
        # =========================================================================================

        # PRODUCT COUNTER AT THE ORDER PAGE
        if '+' in callback.data or '-' in callback.data:
            await products.product_counter(user_id, msg_id, callback, bot)

        # ADD PRODUCT TO BASKET
        if 'basket_add' in callback.data:
            await products.add(user_id, msg_id, callback, bot)

        # ADMIN PAGE CALLBACKS
        # =========================================================================================

        if callback.data == 'admin_employees':
            await employees.show_page(user_id, msg_id, bot)

        if callback.data == 'admin_menu':
            await edit_menu.show_page(user_id, msg_id, bot)

        if callback.data == 'admin_xlsx':
            await admin.get_xlsx(user_id)

        if callback.data == 'admin_error':
            await admin.get_error(callback)

        if callback.data == 'admin_settings':
            await settings.show_page(user_id, msg_id, bot)

        if 'state_bot' in callback.data:
            await settings.switch_state(user_id, msg_id, callback, bot)

        if callback.data == 'admin_stats':
            await admin.show_page(user_id, msg_id, bot, show_stats=True)

        if callback.data == 'change_main_image':
            await settings.change_main_image(user_id, msg_id, callback, bot)

        # MAILS CALLBACKS
        # =========================================================================================

        if callback.data == 'admin_mails':
            await mail.show_page(user_id, msg_id, bot)

        if 'my_mails' in callback.data:
            await mail.get_mails(user_id, msg_id, callback, bot)

        if callback.data == 'create_mail':
            await mail.create(user_id, bot)

        if callback.data == 'mails_help':
            await mail.show_page(user_id, msg_id, bot, show_help=True)

        if 'delete_mail' in callback.data:
            await mail.delete(user_id, msg_id, callback, bot)

        if 'send_mail' in callback.data:
            await mail.send(user_id, msg_id, callback, bot)

        if callback.data == 'back':
            await admin.show_page(user_id, msg_id, bot)

        # EMPLOYEES CALLBACKS
        # =========================================================================================

        if callback.data == 'update_password':
            await employees.show_page(user_id, msg_id, bot, update_pw=True)

        if 'delete_employee' in callback.data:
            await employees.delete(user_id, msg_id, callback, bot)

        if callback.data == 'employee_help':
            await employees.show_page(user_id, msg_id, bot, show_help=True)

        # EDIT MENU CALLBACKS
        # =========================================================================================

        if 'change_desc' in callback.data:
            await edit_menu.change_desc(user_id, callback, bot)

        if 'change_image' in callback.data:
            await edit_menu.change_image(user_id, callback, bot)

        if 'change_price' in callback.data:
            await edit_menu.change_price(user_id, callback, bot)

        if callback.data == 'add_product_page':
            await edit_menu.add_product(user_id, callback, bot)

        if callback.data == 'del_product_page':
            await edit_menu.show_page(user_id, msg_id, bot, del_product=True)

        if 'delete_product' in callback.data:
            await edit_menu.delete_product(user_id, msg_id, callback, bot)

        if callback.data == 'menu_help':
            await edit_menu.show_page(user_id, msg_id, bot, show_help=True)

        if 'menu_page' in callback.data:
            await edit_menu.pagination(user_id, msg_id, callback, bot)

        if callback.data == 'back_to_edit_menu':
            await edit_menu.show_page(user_id, msg_id, bot)

        # MY ORDERS CALLBACKS
        # =========================================================================================

        if 'my_orders' in callback.data:
            await my_orders.pagination(user_id, msg_id, callback, bot)

    except aiogram.utils.exceptions.MessageNotModified:
        pass
    await callback.answer()


async def cancel_callback(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    if callback.data == 'cancel':
        await callback.answer('Ввод отменён', show_alert=True)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)

    if callback.data == 'without_image':
        product_list = await edit_menu.get_product_list()
        if len(product_list) == 3:
            product_list.append(None)
        await database.add_product(product_list)

        await bot.send_message(
            chat_id=callback.from_user.id,
            text='✅ Товар добавлен\n\n' + EDIT_MENU_TITLE,
            reply_markup=await edit_menu.get_page(False)
        )

    await state.finish()
    await callback.answer()
