from datetime import datetime
import qrcode
import os

import aiogram.utils.exceptions
from aiogram import Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InputFile
from aiogram.types import PreCheckoutQuery
from aiogram.types.message import ContentType

import callbacks
import commands
import pages
from config import API_TOKEN
from functions import *
from markups import *
from messages import *
from order_db import OrderDB
from states import *

bot = Bot(API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class ProductList:
    product_list = []

    @classmethod
    async def append_product_list(cls, product):
        cls.product_list.append(product)

    @classmethod
    async def get_product_list(cls):
        return cls.product_list

    @classmethod
    async def clear_product_list(cls):
        cls.product_list.clear()


@dp.message_handler(commands=['start', 'new'])
async def start_command(message: types.Message):
    await commands.start_command(bot, message)


@dp.message_handler(lambda message: message.text and 'панель управления' in message.text.lower()
                    or 'admin' in message.text.lower())
async def admin_login(message: types.Message):
    await commands.admin_login(message)


@dp.message_handler(commands=['my_orders'])
async def my_orders(message: types.Message):
    await callbacks.my_orders(message, bot, message.from_user.id, message.message_id)


@dp.message_handler(commands=['backup'])
async def admin_backup(message: types.Message):
    await commands.admin_backup(message)


@dp.message_handler(commands=['error'])
async def get_error_msg(message: types.Message):
    await commands.get_error_msg(message)


@dp.message_handler(lambda message: message.text and 'список заказов' in message.text.lower()
                    or 'personal' in message.text.lower())
async def employee_command(message: types.Message):
    employees_list = await OrderDB.get_id_by_status('Повар')

    if message.from_user.id in employees_list:
        await get_24h_orders_list(message)
    else:
        await Logging.employee_password.set()
        await message.answer('Введите пароль:', reply_markup=ikb_cancel)
    await message.delete()


@dp.message_handler(state=Logging.admin_password)
async def check_admin_password_dialog(message: types.Message, state: FSMContext):
    if message.text == '123':
        await OrderDB.add_employee(message.from_user.id, message.from_user.full_name, 'Admin')
        await message.answer('Успешная авторизация', reply_markup=rkb_admin)
        await message.answer(ADMIN_TITLE, reply_markup=ikb_admin)
        await state.finish()
    await message.delete()


@dp.message_handler(state=Logging.employee_password)
async def check_employee_password_dialog(message: types.Message, state: FSMContext):
    if message.text.upper() == get_json('data.json')['employee_password']:
        await OrderDB.add_employee(message.from_user.id, message.from_user.full_name, 'Повар')
        update_password()
        await message.answer(EMPLOYEE_MESSAGE, reply_markup=rkb_employee)
        await state.finish()
    await message.delete()


@dp.message_handler(state=ChangeProduct.get_new_desc)
async def change_product_desc(message: types.Message, state: FSMContext):
    product = await ChangeProduct.get_product()
    await OrderDB.set_product_desc(message.text, product)
    await bot.send_message(message.from_user.id, '✅ Описание изменено\n\n' + EDIT_MENU_TITLE,
                           reply_markup=await pages.edit_menu_page(False))
    await state.finish()
    await message.delete()


@dp.message_handler(state=ChangeProduct.get_new_product_image)
async def change_product_image(message: types.Message, state: FSMContext):
    try:
        await bot.send_photo(message.from_user.id, photo=message.text)
        await bot.send_message(message.from_user.id, '✅ Изображение установлено\n\n'+EDIT_MENU_TITLE,
                               reply_markup=await pages.edit_menu_page(False))
        await OrderDB.set_product_image(message.text, await ChangeProduct.get_product())
        await state.finish()
    except (aiogram.utils.exceptions.WrongFileIdentifier, aiogram.utils.exceptions.BadRequest, TypeError):
        await bot.send_message(message.from_user.id, 'Неверная ссылка, изображение ненайдено', reply_markup=ikb_cancel)
    await message.delete()


@dp.message_handler(state=ChangeProduct.get_new_price)
async def change_product_price(message: types.Message, state: FSMContext):
    if len(message.text) < 6:
        for ch in message.text:
            if ch not in string.digits:
                return
        await OrderDB.set_product_price(int(message.text), await ChangeProduct.get_product())
        await bot.send_message(message.from_user.id, '✅ Цена изменена\n\n'+EDIT_MENU_TITLE,
                               reply_markup=await pages.edit_menu_page(False))
        await state.finish()
    await message.delete()


@dp.message_handler(state=AddProduct.get_name)
async def add_product_name(message: types.Message):
    if len(message.text) > 1:
        await bot.send_message(message.from_user.id, 'Введите стоимость товара:', reply_markup=ikb_cancel)
        await ProductList.append_product_list(message.text)
        await AddProduct.get_price.set()
    await message.delete()


@dp.message_handler(state=AddProduct.get_price)
async def add_product_price(message: types.Message):
    try:
        if int(message.text) >= 0:
            await bot.send_message(message.from_user.id, 'Введите состав:', reply_markup=ikb_cancel)
            await ProductList.append_product_list(int(message.text))
            await AddProduct.get_desc.set()
    except ValueError:
        pass
    await message.delete()


@dp.message_handler(state=AddProduct.get_desc)
async def add_product_desc(message: types.Message):
    await ProductList.append_product_list(message.text)
    await bot.send_message(message.from_user.id, 'Введите ссылку на изображение:', reply_markup=ikb_add_image)
    await AddProduct.get_image.set()
    await message.delete()


@dp.message_handler(state=AddProduct.get_image)
async def add_product_image(message: types.Message, state: FSMContext):
    await ProductList.append_product_list(message.text)
    await OrderDB.add_product(await ProductList.get_product_list())
    await bot.send_message(message.from_user.id, '✅ Товар добавлен\n\n'+EDIT_MENU_TITLE,
                           reply_markup=await pages.edit_menu_page(False))
    await ProductList.clear_product_list()
    await state.finish()
    await message.delete()


@dp.message_handler(state=ChangeMainImage.get_main_image)
async def change_main_image(message: types.Message, state: FSMContext):
    try:
        await bot.send_photo(message.from_user.id, photo=message.text)
        await bot.send_message(message.from_user.id, '✅ Изображение установлено\n\n'+SETTINGS_TITLE,
                               reply_markup=await pages.settings_page())
        await OrderDB.set_url('main_image', message.text)
        await state.finish()
    except (aiogram.utils.exceptions.WrongFileIdentifier, aiogram.utils.exceptions.BadRequest, TypeError):
        await bot.send_message(message.from_user.id, 'Неверная ссылка, изображение не найдено', reply_markup=ikb_cancel)
    await message.delete()


@dp.message_handler(state=OrderComment.get_comment)
async def set_comment(message: types.Message, state: FSMContext):
    await OrderDB.set_comment(message.from_user.id, message.text)
    await state.finish()
    await message.delete()
    await bot.send_message(message.from_user.id, await basket_title(message.from_user.id),
                           reply_markup=await pages.basket_menu_page(message.from_user.id))


@dp.message_handler(state=ErrorHandler.get_error)
async def get_error_handler(message: types.Message, state: FSMContext):
    if len(message.text) > 5:
        await error_to_db(message, bot)
        await state.finish()
    await message.delete()


@dp.message_handler(state=Mail.new_mail)
async def get_mail_msg(message: types.Message, state: FSMContext):
    if len(message.text) > 5:
        await OrderDB.insert_mail(message.text)
        mail_id, mail_text = await OrderDB.get_mail()
        await state.finish()
        await message.answer(mail_text, reply_markup=await pages.my_mails(int(mail_id)))
    await message.delete()


@dp.message_handler()
async def message_filter(message: types.Message):
    products = await OrderDB.get_prices()
    for product in products:
        if message.text == product[0]:
            try:
                await bot.send_photo(message.from_user.id,
                                     photo=product[3],
                                     caption=f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                                     reply_markup=await pages.product_page(message.from_user.id, product[0]))
            except aiogram.utils.exceptions.BadRequest:
                await bot.send_message(message.from_user.id,
                                       f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                                       reply_markup=await pages.product_page(message.from_user.id, product[0]))

            await OrderDB.add_temp(message.from_user.id, product[0])
    await message.delete()


@dp.inline_handler(text='#menu')
async def inline_h(query: types.InlineQuery):
    if get_json('data.json')['is_bot_enabled']:
        item_list = []
        for product in await OrderDB.get_prices():
            product = list(product)
            if query.chat_type == 'sender':
                msg = InputTextMessageContent(product[0])
            else:
                msg = InputTextMessageContent(PRIVATE_MESSAGE)
            if product[2] is None:
                product[2] = ''
            item_list.append(InlineQueryResultArticle(id=generate_id(),
                                                      input_message_content=msg,
                                                      title=product[0],
                                                      thumb_url=product[3],
                                                      description=f'Состав: {product[2]}\nЦена: {product[1]}₽'))

        await bot.answer_inline_query(query.id, item_list, cache_time=1)
    else:
        await bot.send_message(query.from_user.id, PAUSE_MESSAGE)


@dp.callback_query_handler(state=[Logging.admin_password, Logging.employee_password, ChangeProduct.get_new_desc,
                                  ChangeProduct.get_new_product_image, ChangeProduct.get_new_price,
                                  AddProduct.get_price, AddProduct.get_image, AddProduct.get_name, AddProduct.get_desc,
                                  ChangeMainImage.get_main_image, OrderComment.get_comment, ErrorHandler.get_error,
                                  Mail.new_mail])
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    await callbacks.cancel_callback(callback, bot, state, ProductList)


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    msg_id = callback.message.message_id

# BASKET PAGE CALLBACKS
# ======================================================================================================================
    try:
        if 'set_time' in callback.data:
            await callbacks.set_order_time(user_id, msg_id, callback, bot)

        if callback.data == 'order_comment':
            await callbacks.set_order_comment(user_id, msg_id, bot, OrderComment)

        if callback.data == 'pay':
            await callbacks.create_invoice(user_id, msg_id, bot)

        if '!up' in callback.data or '!dn' in callback.data:
            await callbacks.basket_product_counter(user_id, msg_id, callback, bot)

        if 'time_page' in callback.data:
            await callbacks.set_order_time_navigation(user_id, msg_id, callback, bot)

        if 'back_to_basket' in callback.data:
            await callbacks.back_to_basket(user_id, msg_id, callback, bot)

# ORDER PAGE CALLBACKS
# ======================================================================================================================

        if '+' in callback.data or '-' in callback.data:
            await callbacks.order_product_counter(user_id, msg_id, callback, bot)

        if 'basket_add' in callback.data:
            await callbacks.add_to_basket(user_id, msg_id, callback, bot)

        if callback.data == 'basket':
            await callbacks.basket(user_id, callback, bot)


# ADMIN PAGE CALLBACKS
# ======================================================================================================================

        if callback.data == 'admin_employees':
            password = get_json('data.json')
            await bot.edit_message_text(EMPLOYEE_TITLE +
                                        f'\nПароль для персонала: <b>{password["employee_password"]}</b>',
                                        user_id, msg_id, reply_markup=await pages.employees_page())

        if callback.data == 'admin_menu':
            await bot.edit_message_text(EDIT_MENU_TITLE, user_id, msg_id,
                                        reply_markup=await pages.edit_menu_page(False))

        if callback.data == 'admin_xlsx':
            await callbacks.xlsx(user_id, bot)

        if callback.data == 'admin_error':
            await callback.message.answer(ERROR_TITLE, reply_markup=ikb_cancel)
            await ErrorHandler.get_error.set()

        if callback.data == 'admin_settings':
            await bot.edit_message_text(SETTINGS_TITLE, user_id, msg_id, reply_markup=await pages.settings_page())

        if 'state_bot' in callback.data:
            await callbacks.state_bot(user_id, msg_id, callback, bot)

        if callback.data == 'admin_stats':
            await bot.edit_message_text(await admin_stats(), user_id, msg_id, reply_markup=ikb_admin)

        if callback.data == 'change_main_image':
            await bot.edit_message_text('Введите ссылку на изображение:', user_id, msg_id, reply_markup=ikb_cancel)
            await ChangeMainImage.get_main_image.set()
            await callback.answer('Редактирование изображения')

# MAILS CALLBACKS
# ======================================================================================================================

        if callback.data == 'admin_mails':
            await bot.edit_message_text(MAILS_TITLE, user_id, msg_id, reply_markup=await pages.mails_page())

        if 'my_mails' in callback.data:
            await callbacks.my_mails(user_id, msg_id, callback, bot)

        if callback.data == 'create_mail':
            await Mail.new_mail.set()
            await bot.send_message(user_id, 'Введите текст рассылки', reply_markup=ikb_cancel)

        if callback.data == 'mails_help':
            await bot.edit_message_text(MAILS_TITLE + MAILS_HELP, user_id, msg_id,
                                        reply_markup=await pages.mails_page())

        if 'delete_mail' in callback.data:
            await callbacks.delete_mail(user_id, msg_id, callback, bot)

        if 'send_mail' in callback.data:
            await callbacks.send_mail(user_id, msg_id, callback, bot)

        if callback.data == 'back':
            await bot.edit_message_text(ADMIN_TITLE, user_id, msg_id, reply_markup=ikb_admin)


# EDIT EMPLOYEES CALLBACKS
# ======================================================================================================================

        if callback.data == 'change_password':
            pw = update_password()
            await bot.edit_message_text(EMPLOYEE_TITLE + f'\nПароль для персонала: <b>{pw}</b>',
                                        user_id, msg_id, reply_markup=await pages.employees_page())

        if 'remove_employee' in callback.data:
            employee_id = int(callback.data[16:])
            await OrderDB.delete_employee(employee_id)
            await bot.edit_message_text(EMPLOYEE_TITLE, user_id, msg_id, reply_markup=await pages.employees_page())

        if callback.data == 'employee_help':
            password = get_json('data.json')
            await bot.edit_message_text(EMPLOYEE_TITLE +
                                        f'\nПароль для персонала: <b>{password["employee_password"]}</b>\n\n' +
                                        EMPLOYEE_HELP, user_id, msg_id, reply_markup=await pages.employees_page())

# EDIT MENU CALLBACKS
# ======================================================================================================================

        if 'change_desc' in callback.data:
            await callbacks.change_desc(user_id, callback, bot)

        if 'change_image' in callback.data:
            await callbacks.change_image(user_id, callback, bot)

        if 'change_price' in callback.data:
            await callbacks.change_price(user_id, callback, bot)

        if callback.data == 'menu_add':
            await bot.send_message(user_id, 'Введите название товара:', reply_markup=ikb_cancel)
            await AddProduct.get_name.set()
            await callback.answer('Добавление товара')

        if callback.data == 'menu_delete':
            await bot.edit_message_text(EDIT_MENU_TITLE, user_id, msg_id,
                                        reply_markup=await pages.edit_menu_page(True))

        if callback.data == 'menu_help':
            await bot.edit_message_text(EDIT_MENU_TITLE+'\n'+MENU_HELP, user_id, msg_id,
                                        reply_markup=await pages.edit_menu_page(False))

        if 'menu_page' in callback.data:
            del_product = True if 'True' in callback.data else False
            await callbacks.edit_menu_navigation(user_id, msg_id, callback, bot, del_product)

        if 'remove_product' in callback.data:
            await callbacks.remove_product(user_id, msg_id, callback, bot)

        if callback.data == 'back_to_edit_menu':
            await bot.edit_message_text(EDIT_MENU_TITLE, user_id, msg_id,
                                        reply_markup=await pages.edit_menu_page(False))

# MY ORDERS CALLBACKS
# ======================================================================================================================
        if 'my_orders' in callback.data:
            await callbacks.my_orders_navigation(user_id, msg_id, callback, bot)

    except aiogram.utils.exceptions.MessageNotModified:
        pass
    await callback.answer()

# PAYMENT
# ======================================================================================================================


@dp.pre_checkout_query_handler()
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    order_number = await generate_order_number()
    price = int(int(message.successful_payment.total_amount) / 100)
    date = datetime.datetime.now() + datetime.timedelta(hours=TIME_ZONE)
    date = date.strftime("%d.%m.%Y")
    time = await OrderDB.get_order_time(message.from_user.id)
    cur = message.successful_payment.currency
    payload = message.successful_payment.invoice_payload
    order_list = payload
    for ch in ['{', '}', '\'', '"']:
        order_list = order_list.replace(ch, '')
    comment = await OrderDB.get_comment(message.from_user.id)
    order_user_time = await OrderDB.get_order_user_time(message.from_user.id)
    msg = SUCCESSFUL_MESSAGE.format(order_number=order_number, cur=cur, amount=str(price))

    if get_json('data.json')['is_qrcode_enabled']:
        img = qrcode.make(f'http://95.216.65.93:13617/?order={order_number}')
        img_name = f'{order_number}.png'
        img.save(img_name)
        await bot.send_photo(message.from_user.id, InputFile(img_name), caption=msg)
        for file in os.listdir():
            if '.png' in file:
                os.remove(file)
    else:
        await message.answer(msg)

    await OrderDB.clear_basket(message.from_user.id)

    if order_user_time is not None:
        await OrderDB.add_to_archive(message.from_user.id, order_number, order_list, comment, price,
                                     order_user_time)
        user_time_str = f'\n⏱ <b>Приготовить к {order_user_time}</b>\n'
    else:
        await OrderDB.add_to_archive(message.from_user.id, order_number, order_list, comment, price, time)
        user_time_str = ''

    print('{'+f'"user_id": {message.from_user.id}, "order_number": {order_number}, "order_list": {order_list}, '
              f'"price": {price}{cur}, "order_user_time": {order_user_time}, "comment": {comment}, "date": '
              f'{date}, "time": {time}'+'}')

    await send_order_to_employees(comment, payload, bot, order_number, user_time_str, price, date, time)
    await backup(date)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
