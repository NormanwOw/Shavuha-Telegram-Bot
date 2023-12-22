import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext
from aiogram import Bot

from messages import *
from functions import *
from menus import Basket, Product, Employees, EditMenu, Settings, Mail, MyOrders, Admin


@logger.catch
async def handler(user_id: int, msg_id: int, callback: types.CallbackQuery, bot: Bot):
    try:
        # BASKET PAGE CALLBACKS
        # =========================================================================================

        if callback.data == 'basket':
            await Basket.show_page(user_id, msg_id, callback, bot, check_basket=True)

        # SET ORDER TIME PAGE
        if 'set_time' in callback.data:
            await Basket.set_time(user_id, msg_id, callback, bot)

        # ORDER COMMENT PAGE
        if callback.data == 'order_comment':
            await Basket.set_comment(user_id, msg_id, bot)

        if callback.data == 'pay':
            await Basket.get_pay_invoice(user_id, msg_id, bot)

        # PRODUCT COUNTER AT THE BASKET PAGE
        if '!up' in callback.data or '!dn' in callback.data:
            await Basket.product_counter(user_id, msg_id, callback, bot)

        if 'time_page' in callback.data:
            await Basket.show_time_page(user_id, msg_id, callback, bot)

        if 'back_to_basket' in callback.data:
            await Basket.show_page(user_id, msg_id, callback, bot)

        # ORDER PAGE CALLBACKS
        # =========================================================================================

        # PRODUCT COUNTER AT THE ORDER PAGE
        if '+' in callback.data or '-' in callback.data:
            await Product.product_counter(user_id, msg_id, callback, bot)

        # ADD PRODUCT TO BASKET
        if 'basket_add' in callback.data:
            await Product.add(user_id, msg_id, callback, bot)

        # ADMIN PAGE CALLBACKS
        # =========================================================================================

        if callback.data == 'admin_employees':
            await Employees.show_page(user_id, msg_id, bot)

        if callback.data == 'admin_menu':
            await EditMenu.show_page(user_id, msg_id, bot)

        if callback.data == 'admin_xlsx':
            await Admin.get_xlsx(user_id, bot)

        if callback.data == 'admin_error':
            await Admin.get_error(callback)

        if callback.data == 'admin_settings':
            await Settings.show_page(user_id, msg_id, bot)

        if 'state_bot' in callback.data:
            await Settings.switch_state(user_id, msg_id, callback, bot)

        if callback.data == 'admin_stats':
            await Admin.show_page(user_id, msg_id, bot, show_stats=True)

        if callback.data == 'change_main_image':
            await Settings.change_main_image(user_id, msg_id, callback, bot)

        # MAILS CALLBACKS
        # =========================================================================================

        if callback.data == 'admin_mails':
            await Mail.show_page(user_id, msg_id, bot)

        if 'my_mails' in callback.data:
            await Mail.get_mails(user_id, msg_id, callback, bot)

        if callback.data == 'create_mail':
            await Mail.create(user_id, bot)

        if callback.data == 'mails_help':
            await Mail.show_page(user_id, msg_id, bot, show_help=True)

        if 'delete_mail' in callback.data:
            await Mail.delete(user_id, msg_id, callback, bot)

        if 'send_mail' in callback.data:
            await Mail.send(user_id, msg_id, callback, bot)

        if callback.data == 'back':
            await Admin.show_page(user_id, msg_id, bot)

        # EMPLOYEES CALLBACKS
        # =========================================================================================

        if callback.data == 'update_password':
            await Employees.show_page(user_id, msg_id, bot, update_pw=True)

        if 'delete_employee' in callback.data:
            await Employees.delete(user_id, msg_id, callback, bot)

        if callback.data == 'employee_help':
            await Employees.show_page(user_id, msg_id, bot, show_help=True)

        # EDIT MENU CALLBACKS
        # =========================================================================================

        if 'change_desc' in callback.data:
            await EditMenu.change_desc(user_id, callback, bot)

        if 'change_image' in callback.data:
            await EditMenu.change_image(user_id, callback, bot)

        if 'change_price' in callback.data:
            await EditMenu.change_price(user_id, callback, bot)

        if callback.data == 'add_product_page':
            await EditMenu.add_product(user_id, callback, bot)

        if callback.data == 'del_product_page':
            await EditMenu.show_page(user_id, msg_id, bot, del_product=True)

        if 'delete_product' in callback.data:
            await EditMenu.delete_product(user_id, msg_id, callback, bot)

        if callback.data == 'menu_help':
            await EditMenu.show_page(user_id, msg_id, bot, show_help=True)

        if 'menu_page' in callback.data:
            await EditMenu.pagination(user_id, msg_id, callback, bot)

        if callback.data == 'back_to_edit_menu':
            await EditMenu.show_page(user_id, msg_id, bot)

        # MY ORDERS CALLBACKS
        # =========================================================================================

        if 'my_orders' in callback.data:
            await MyOrders.pagination(user_id, msg_id, callback, bot)

    except aiogram.utils.exceptions.MessageNotModified:
        pass
    await callback.answer()


async def cancel_callback(callback: types.CallbackQuery, bot: Bot, state: FSMContext, product):
    if callback.data == 'cancel':
        await callback.answer('Ввод отменён', show_alert=True)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)

    if callback.data == 'without_image':
        product_list = await product.get_product_list()
        if len(product_list) == 3:
            product_list.append(None)
        await OrderDB.add_product(product_list)

        await bot.send_message(
            chat_id=callback.from_user.id,
            text='✅ Товар добавлен\n\n' + EDIT_MENU_TITLE,
            reply_markup=await EditMenu.get_page(False)
        )

    await state.finish()
    await callback.answer()
