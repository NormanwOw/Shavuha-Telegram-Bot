import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext

from messages import *
from functions import *
from markups import *
from states import *
from menus import Basket, Product, Employees, EditMenu, Settings, Mail, MyOrders, Admin


@logger.catch
async def handler(user_id: int, msg_id: int, callback: types.CallbackQuery, bot: Bot):
    try:
        # BASKET PAGE CALLBACKS
        # =========================================================================================

        if callback.data == 'basket':
            await Basket.show_page(user_id, callback, bot)

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
            await Basket.back_to_page(user_id, msg_id, callback, bot)

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
            product = callback.data[12:]
            await ChangeProduct.set_product(product)
            await ChangeProduct.get_new_desc.set()

            await bot.send_message(
                chat_id=user_id,
                text='Введите описание товара (состав):',
                reply_markup=ikb_cancel
            )

            await callback.answer('Редактирование описания')

        if 'change_image' in callback.data:
            product = callback.data[13:]
            await ChangeProduct.set_product(product)
            await ChangeProduct.get_new_product_image.set()

            await bot.send_message(
                chat_id=user_id,
                text='Отправьте ссылку на изображение:',
                reply_markup=ikb_cancel
            )

            await callback.answer('Редактирование изображения')

        if 'change_price' in callback.data:
            product = callback.data[13:]
            await ChangeProduct.set_product(product)
            await ChangeProduct.get_new_price.set()

            await bot.send_message(
                chat_id=user_id,
                text='Введите стоимость товара:',
                reply_markup=ikb_cancel
            )

            await callback.answer('Редактирование цены')

        if callback.data == 'menu_add':
            await bot.send_message(
                chat_id=user_id,
                text='Введите название товара:',
                reply_markup=ikb_cancel
            )

            await AddProduct.get_name.set()
            await callback.answer('Добавление товара')

        if callback.data == 'menu_delete':
            await bot.edit_message_text(
                text=EDIT_MENU_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await EditMenu.get_page(True)
            )

        if callback.data == 'menu_help':
            await bot.edit_message_text(
                text=EDIT_MENU_TITLE + '\n' + MENU_HELP,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await EditMenu.get_page(False)
            )

        if 'menu_page' in callback.data:
            del_product = True if 'True' in callback.data else False
            data = callback.data.split()
            page = int(data[1])
            next_page_len = int(data[2])

            if 'next' in callback.data and next_page_len > 0:
                await bot.edit_message_text(
                    text=EDIT_MENU_TITLE,
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await EditMenu.get_page(del_product, page + 1)
                )

            elif 'prev' in callback.data and page != 1:
                await bot.edit_message_text(
                    text=EDIT_MENU_TITLE,
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await EditMenu.get_page(del_product, page - 1)
                )

        if 'remove_product' in callback.data:
            product = callback.data[15:]
            await OrderDB.delete_product(product)

            await bot.edit_message_text(
                text=EDIT_MENU_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await EditMenu.get_page(True)
            )
            await callback.answer(f'Товар удалён', show_alert=True)

        if callback.data == 'back_to_edit_menu':
            await bot.edit_message_text(
                text=EDIT_MENU_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await EditMenu.get_page(False)
            )

        # MY ORDERS CALLBACKS
        # =========================================================================================

        if 'my_orders' in callback.data:
            data = callback.data.split()
            page = int(data[1])
            if 'prev' in callback.data:
                if page != 1:
                    await my_orders(callback, bot, user_id, msg_id, page - 1)
            else:
                total_pages = int(data[2])
                if page != total_pages:
                    await my_orders(callback, bot, user_id, msg_id, page + 1)

    except aiogram.utils.exceptions.MessageNotModified:
        pass
    await callback.answer()


async def cancel_callback(callback: types.CallbackQuery, bot: Bot, state: FSMContext, product):
    if callback.data == 'cancel':
        await callback.answer('Ввод отменён', show_alert=True)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)

    if callback.data == 'without_image':
        product_list = product.get_product_list()
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


async def my_orders(message, bot: Bot, user_id: int, msg_id: int, selected_page: int = 0):
    user_orders = await OrderDB.get_user_orders(message.from_user.id)
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
                    text=await user_orders_page(
                        last_page, selected_page, user_orders_count, user_orders
                    ),
                    reply_markup=await MyOrders.get_page(total_pages, total_pages)
                )
            else:
                await bot.edit_message_text(
                    text=await user_orders_page(
                        last_page, selected_page, user_orders_count, user_orders
                    ),
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await MyOrders.get_page(selected_page, total_pages)
                )
        else:
            if selected_page == 0:
                await message.answer(await user_orders_page(
                    user_orders_count, selected_page, user_orders_count, user_orders
                )
                                     )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=await user_orders_page(
                        user_orders_count, selected_page, user_orders_count, user_orders
                    )
                )
    else:
        await bot.send_message(
            chat_id=user_id,
            text='Список заказов пуст'
        )
