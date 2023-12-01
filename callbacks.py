import os

from aiogram.types import LabeledPrice
import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext

from config import PAY_TOKEN
from messages import *
from functions import *
from markups import *
from states import *
import pages


@logger.catch
async def handler(user_id: int, msg_id: int, callback: types.CallbackQuery, bot: Bot):
    # BASKET PAGE CALLBACKS
    # =============================================================================================
    try:
        if 'set_time' in callback.data:
            if callback.data == 'set_time':
                time, hour, minute = await get_time()

                await bot.edit_message_text(
                    text=SET_TIME_MESSAGE,
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.set_time_page(user_id, hour, minute)
                )

                await OrderDB.set_order_time(user_id, time)
            elif callback.data == 'cancel_set_time':
                if await OrderDB.get_order_user_time(user_id) is None:
                    await callback.answer()
                    return

                await OrderDB.set_order_user_time(user_id, None)

                await bot.edit_message_text(
                    text=await basket_title(user_id),
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.basket_menu_page(user_id)
                )

                await callback.answer('Точное время отменено')
            else:
                time = callback.data[9:]
                await callback.answer(time)
                await OrderDB.set_order_user_time(user_id, time)

                await bot.edit_message_text(
                    text=await basket_title(user_id),
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.basket_menu_page(user_id)
                )

        if callback.data == 'order_comment':
            if await OrderDB.get_comment(user_id) is None:

                await bot.send_message(
                    chat_id=user_id,
                    text='Комментарий к заказу:',
                    reply_markup=ikb_cancel
                )

                await OrderComment.get_comment.set()
            else:
                await bot.edit_message_text(
                    text=await order_comment_title(user_id),
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.comment_page()
                )

        # CREATE PAY INVOICE
        if callback.data == 'pay':
            data = await OrderDB.get_order_by_id(user_id)
            try:
                order_list = json.loads(data[2])
            except TypeError:
                await bot.delete_message(user_id, msg_id)
                return
            order_prices = []

            prices = await OrderDB.get_prices()
            desc = ''
            p = ''
            for item in order_list:
                for i in prices:
                    if i[0] == item:
                        p = i[1]
                cnt = order_list[item]
                label = item + f' - {cnt}шт.'
                lp = LabeledPrice(label=label, amount=p * cnt * 100)
                order_prices.append(lp)

                desc += f' ▫️ {item}'

            await bot.send_invoice(
                chat_id=user_id,
                title='Заказ',
                description=desc,
                provider_token=PAY_TOKEN,
                currency='rub',
                start_parameter='example',
                payload=order_list,
                prices=order_prices,
                need_shipping_address=False
            )

        # PRODUCT COUNTER AT THE BASKET PAGE
        if '!up' in callback.data or '!dn' in callback.data:
            product = callback.data[4:]
            if '!up' in callback.data:
                count = 1
            else:
                count = -1
            await OrderDB.add_order(user_id, {product: count})

            if await OrderDB.get_products_count(user_id) == 0:
                await OrderDB.clear_basket(user_id)

                await bot.edit_message_text(
                    text=EMPTY_BASKET,
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.basket_menu_page(user_id)
                )

                return

            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.basket_menu_page(user_id)
            )

        # SHOW ORDER TIME PAGE
        if 'time_page' in callback.data:
            _, hour, minute = await get_time()
            if 'next' in callback.data:
                hour += 6
            try:
                await bot.edit_message_reply_markup(
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.set_time_page(user_id, hour, minute)
                )

            except aiogram.utils.exceptions.MessageNotModified:
                await callback.answer()
                return

        # SHOW BASKET PAGE
        if 'back_to_basket' in callback.data:
            if 'del' in callback.data:
                await OrderDB.delete_comment(user_id)
                await callback.answer('Комментарий удалён')

            await bot.edit_message_text(
                text=await basket_title(user_id),
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.basket_menu_page(user_id)
            )

        # ORDER PAGE CALLBACKS
        # =========================================================================================

        # PRODUCT COUNTER AT THE ORDER PAGE
        if '+' in callback.data or '-' in callback.data:
            count = await OrderDB.get_count(user_id)
            product = callback.data[1:]
            if await OrderDB.is_temp_exists(user_id) is False:
                await OrderDB.add_temp(user_id, product)
            else:
                if '+' in callback.data:
                    if count > 21:
                        await callback.answer()
                        return
                    await OrderDB.set_count(user_id, count + 1)
                else:
                    if count == 1:
                        await callback.answer()
                        return
                    await OrderDB.set_count(user_id, count - 1)

            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.product_page(user_id, product)
            )

        if 'basket_add' in callback.data:
            product = callback.data[11:]
            time = await get_time()
            await OrderDB.temp_to_order(user_id)
            await OrderDB.set_order_time(user_id, time[0])
            await callback.answer('Товар добавлен в корзину')

            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.product_page(user_id, product)
            )

        if callback.data == 'basket':
            if await OrderDB.get_order_by_id(user_id) is None:
                await callback.answer('Корзина пуста')
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=await basket_title(user_id),
                    reply_markup=await pages.basket_menu_page(user_id)
                )

        # ADMIN PAGE CALLBACKS
        # ======================================================================================================================

        if callback.data == 'admin_employees':
            password = get_json('data.json')

            await bot.edit_message_text(
                text=EMPLOYEE_TITLE + f'\nПароль для персонала: '
                                      f'<b>{password["employee_password"]}</b>',
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.employees_page()
            )

        if callback.data == 'admin_menu':
            await bot.edit_message_text(
                text=EDIT_MENU_TITLE,
                chat_id = user_id,
                message_id = msg_id,
                reply_markup=await pages.edit_menu_page(False)
            )

        if callback.data == 'admin_xlsx':
            doc = await get_xlsx()
            await bot.send_document(user_id, open(doc, 'rb'))
            for file in os.listdir():
                if '.xlsx' in file:
                    os.remove(file)

        if callback.data == 'admin_error':
            await callback.message.answer(
                text=ERROR_TITLE,
                reply_markup=ikb_cancel
            )
            await ErrorHandler.get_error.set()

        if callback.data == 'admin_settings':
            await bot.edit_message_text(
                text=SETTINGS_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.settings_page()
            )

        if 'state_bot' in callback.data:
            if 'off' in callback.data:
                await set_json('data.json', {'is_bot_enabled': 0})
                await callback.answer('Приём заказов остановлен', show_alert=True)
            else:
                await set_json('data.json', {'is_bot_enabled': 1})
                await callback.answer('Приём заказов запущен', show_alert=True)

            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.settings_page()
            )

        if callback.data == 'admin_stats':
            await bot.edit_message_text(
                text=await admin_stats(),
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=ikb_admin
            )

        if callback.data == 'change_main_image':
            await bot.edit_message_text(
                text='Отправьте изображение:',
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=ikb_cancel
            )
            await ChangeMainImage.get_main_image.set()
            await callback.answer('Редактирование изображения')

        # MAILS CALLBACKS
        # ======================================================================================================================

        if callback.data == 'admin_mails':
            await bot.edit_message_text(
                text=MAILS_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.mails_page()
            )

        if 'my_mails' in callback.data:
            data = callback.data.split()
            if 'prev' in callback.data:
                page = int(data[1])
                if page == 1:
                    return await callback.answer()
                await OrderDB.move_selected_mail(False)
                page -= 1
            elif 'next' in callback.data:
                page = int(data[1])
                total_pages = int(data[2])
                if page == total_pages:
                    return await callback.answer()
                await OrderDB.move_selected_mail(True)
                page += 1
            try:
                mail_id, mail_text = await OrderDB.get_mail()

                await bot.edit_message_text(
                    text=mail_text,
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.my_mails(mail_id)
                )
            except TypeError:
                await callback.answer('Список рассылок пуст')

        if callback.data == 'create_mail':
            await Mail.new_mail.set()
            await bot.send_message(
                chat_id=user_id,
                text='Введите текст рассылки',
                reply_markup=ikb_cancel
            )

        if callback.data == 'mails_help':
            await bot.edit_message_text(
                text=MAILS_TITLE + MAILS_HELP,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.mails_page()
            )

        if 'delete_mail' in callback.data:
            if 'yes' in callback.data:
                state = await OrderDB.delete_mail()
                await callback.answer('Рассылка удалена', show_alert=True)
                if state:
                    mail_id, mail_text = await OrderDB.get_mail()

                    await bot.edit_message_text(
                        text=mail_text,
                        chat_id=user_id,
                        message_id=msg_id,
                        reply_markup=await pages.my_mails(mail_id)
                    )
                else:
                    await bot.edit_message_text(
                        text=MAILS_TITLE,
                        chat_id=user_id,
                        message_id=msg_id,
                        reply_markup=await pages.mails_page()
                    )
            elif 'no' in callback.data:
                await callback.answer('Удаление отменено', show_alert=True)
                await bot.delete_message(user_id, msg_id)
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text='Удалить рассылку?',
                    reply_markup=ikb_del_mail
                )

        if 'send_mail' in callback.data:
            if 'yes' in callback.data:
                users = await OrderDB.get_all_user_id()
                _, mail_text = await OrderDB.get_mail()
                if users:
                    for user in users:

                        await bot.send_message(
                            chat_id=user,
                            text=mail_text
                        )

                    word = 'клиенту' if str(len(users))[-1] == '1' else 'клиентам'

                    await callback.answer(
                        f'Рассылка успешно отправлена {len(users)} {word}',
                        show_alert=True
                    )

                    await bot.delete_message(user_id, msg_id)
                else:
                    await callback.answer('Список клиентов пуст', show_alert=True)
                    await bot.delete_message(user_id, msg_id)

            elif 'no' in callback.data:
                await callback.answer('Отправление отменено', show_alert=True)
                await bot.delete_message(user_id, msg_id)
            else:
                mail_text = await OrderDB.get_mail()

                await bot.send_message(
                    chat_id=user_id,
                    text=SEND_MAIL + mail_text[1],
                    reply_markup=ikb_send_mail
                )

        if callback.data == 'back':
            await bot.edit_message_text(
                text=ADMIN_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=ikb_admin
            )

        # EDIT EMPLOYEES CALLBACKS
        # ======================================================================================================================

        if callback.data == 'change_password':
            pw = await update_password()

            await bot.edit_message_text(
                text=EMPLOYEE_TITLE + f'\nПароль для персонала: <b>{pw}</b>',
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.employees_page()
            )

        if 'remove_employee' in callback.data:
            employee_id = int(callback.data[16:])
            await OrderDB.delete_employee(employee_id)

            await bot.edit_message_text(
                text=EMPLOYEE_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.employees_page()
            )

        if callback.data == 'employee_help':
            password = get_json('data.json')

            await bot.edit_message_text(
                text=EMPLOYEE_TITLE + f'\nПароль для персонала: '
                                      f'<b>{password["employee_password"]}</b>\n'
                                      f'\n' + EMPLOYEE_HELP,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.employees_page()
            )

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
                reply_markup=await pages.edit_menu_page(True)
            )

        if callback.data == 'menu_help':
            await bot.edit_message_text(
                text=EDIT_MENU_TITLE + '\n' + MENU_HELP,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.edit_menu_page(False)
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
                    reply_markup=await pages.edit_menu_page(del_product, page + 1)
                )

            elif 'prev' in callback.data and page != 1:
                await bot.edit_message_text(
                    text=EDIT_MENU_TITLE,
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.edit_menu_page(del_product, page - 1)
                )

        if 'remove_product' in callback.data:
            product = callback.data[15:]

            await bot.edit_message_text(
                text=EDIT_MENU_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.edit_menu_page(True)
            )

            await callback.answer(f'Товар удалён', show_alert=True)
            await OrderDB.delete_product(product)

        if callback.data == 'back_to_edit_menu':
            await bot.edit_message_text(
                text=EDIT_MENU_TITLE,
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=await pages.edit_menu_page(False)
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
            reply_markup=await pages.edit_menu_page(False)
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
                    reply_markup=await pages.my_orders_navigation(total_pages, total_pages)
                )
            else:
                await bot.edit_message_text(
                    text=await user_orders_page(
                        last_page, selected_page, user_orders_count, user_orders
                    ),
                    chat_id=user_id,
                    message_id=msg_id,
                    reply_markup=await pages.my_orders_navigation(selected_page, total_pages)
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
                        user_orders_count, selected_page, user_orders_count,user_orders
                    )
                )
    else:
        if selected_page == 0:
            await message.answer('Список заказов пуст')
        else:

            await bot.send_message(
                chat_id=user_id,
                text='Список заказов пуст'
            )

    if selected_page == 0:
        await bot.delete_message(user_id, msg_id)
