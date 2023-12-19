from datetime import datetime

import aiogram.utils.exceptions
from aiogram import Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
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
    def append_product_list(cls, item):
        cls.product_list.append(item)

    @classmethod
    def get_product_list(cls):
        return cls.product_list

    @classmethod
    def clear_product_list(cls):
        cls.product_list.clear()


@dp.message_handler(commands=['start', 'new'])
async def start_command(message: types.Message):
    await commands.start_command(bot, message)


@dp.message_handler(
    lambda message: message.text and 'панель управления' in message.text.lower()
    or 'admin' in message.text.lower()
)
async def admin_login(message: types.Message):
    """
    Admin handler
    Show admin panel or Login
    """
    await commands.admin_login(message)


@dp.message_handler(commands=['my_orders'])
async def my_orders(message: types.Message):
    """
    User handler
    Show order list
    """
    await callbacks.my_orders(message, bot, message.from_user.id, message.message_id)
    await bot.delete_message(message.from_user.id, message.message_id)


@dp.message_handler(commands=['error'])
async def get_error_msg(message: types.Message):
    """
    User handler
    Get message from user with some problem
    """
    await commands.get_error_msg(message)


@dp.message_handler(state=ErrorHandler.get_error)
async def get_error_handler(message: types.Message, state: FSMContext):
    """
    Error
    State of getting error message from user
    """
    if len(message.text) > 5:
        await error_to_db(message, bot)
        await state.finish()
    await message.delete()


@dp.message_handler(
    lambda message: message.text and 'список заказов' in message.text.lower()
    or 'personal' in message.text.lower()
)
async def employee_command(message: types.Message):
    """
    Employee handler
    Show orders list or Login
    """
    employees_list = await OrderDB.get_id_by_status('Повар')

    if message.from_user.id in employees_list:
        await get_24h_orders_list(message)
    else:
        await Login.employee_password.set()
        await message.answer('Введите пароль:', reply_markup=ikb_cancel)
    await message.delete()


@dp.message_handler(state=Login.admin_password)
async def check_admin_password_dialog(message: types.Message, state: FSMContext):
    """
    Login
    State of getting admin password
    """
    if message.text == '123':
        await OrderDB.add_employee(message.from_user.id, message.from_user.full_name, 'Admin')
        await message.answer('Успешная авторизация', reply_markup=rkb_admin)
        await message.answer(ADMIN_TITLE, reply_markup=ikb_admin)
        await state.finish()
    await message.delete()


@dp.message_handler(state=Login.employee_password)
async def check_employee_password_dialog(message: types.Message, state: FSMContext):
    """
    Login
    State of getting employee password
    """
    if message.text.upper() == get_json('data.json')['employee_password']:
        await OrderDB.add_employee(message.from_user.id, message.from_user.full_name, 'Повар')
        await update_password()
        await message.answer(EMPLOYEE_MESSAGE, reply_markup=rkb_employee)
        await state.finish()
    await message.delete()


@dp.message_handler(state=ChangeProduct.get_new_desc)
async def change_product_desc(message: types.Message, state: FSMContext):
    """
    Change product
    State of getting new description
    """
    product = await ChangeProduct.get_product()
    await OrderDB.set_product_desc(message.text, product)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='✅ Описание изменено\n\n' + EDIT_MENU_TITLE,
        reply_markup=await pages.edit_menu_page(False)
    )

    await state.finish()
    await message.delete()


@dp.message_handler(state=ChangeProduct.get_new_product_image)
async def change_product_image(message: types.Message, state: FSMContext):
    """
    Change product
    State of getting new image
    """
    product = await ChangeProduct.get_product()
    try:
        await bot.send_photo(
            message.from_user.id,
            message.text,
            '✅ Изображение установлено'
        )

        await message.answer(EDIT_MENU_TITLE, reply_markup=await pages.edit_menu_page(False))
        await OrderDB.set_product_image(message.text, product)
        await state.finish()
    except aiogram.utils.exceptions.BadRequest:

        await bot.send_message(
            chat_id=message.from_user.id,
            text='Неверная ссылка, изображение не найдено',
            reply_markup=ikb_cancel
        )

    await message.delete()


@dp.message_handler(state=ChangeProduct.get_new_price)
async def change_product_price(message: types.Message, state: FSMContext):
    """
    Change product
    State of getting new price
    """
    if len(message.text) < 6:
        for ch in message.text:
            if ch not in string.digits:
                return
        await OrderDB.set_product_price(int(message.text), await ChangeProduct.get_product())

        await bot.send_message(
            chat_id=message.from_user.id,
            text='✅ Цена изменена\n\n' + EDIT_MENU_TITLE,
            reply_markup=await pages.edit_menu_page(False)
        )

        await state.finish()
    await message.delete()


@dp.message_handler(state=AddProduct.get_name)
async def add_product_name(message: types.Message):
    """
    Add new product
    State of getting product name
    """
    if len(message.text) > 1:
        await bot.send_message(
            message.from_user.id,
            'Введите стоимость товара:',
            reply_markup=ikb_cancel
        )

        ProductList.append_product_list(message.text)
        await AddProduct.get_price.set()
    await message.delete()


@dp.message_handler(state=AddProduct.get_price)
async def add_product_price(message: types.Message):
    """
    Add new product
    State of getting product price
    """
    try:
        if int(message.text) >= 0:
            await bot.send_message(
                message.from_user.id,
                'Введите состав:',
                reply_markup=ikb_cancel
            )

            ProductList.append_product_list(int(message.text))
            await AddProduct.get_desc.set()
    except ValueError:
        pass
    await message.delete()


@dp.message_handler(state=AddProduct.get_desc)
async def add_product_desc(message: types.Message):
    """
    Add new product
    State of getting product description
    """
    ProductList.append_product_list(message.text)

    await bot.send_message(
        message.from_user.id,
        'Отправьте изображение:',
        reply_markup=ikb_add_image
    )

    await AddProduct.get_image.set()
    await message.delete()


@dp.message_handler(state=AddProduct.get_image)
async def add_product_image(message: types.Message, state: FSMContext):
    """
    Add new product
    State of getting product image
    """
    try:
        await bot.send_photo(message.from_user.id, message.text)

        await bot.send_message(
            message.from_user.id,
            '✅ Товар добавлен\n\n' + EDIT_MENU_TITLE,
            reply_markup=await pages.edit_menu_page(False)
        )

        ProductList.append_product_list(message.text)
        await OrderDB.add_product(ProductList.get_product_list())
        ProductList.clear_product_list()
        await state.finish()
    except aiogram.utils.exceptions.BadRequest:

        await bot.send_message(
            message.from_user.id,
            'Неверная ссылка, изображение не найдено',
            reply_markup=ikb_cancel
        )

    await message.delete()


@dp.message_handler(state=ChangeMainImage.get_main_image)
async def change_main_image(message: types.Message, state: FSMContext):
    """
    Change main image
    State of getting main image
    """
    try:
        await bot.send_photo(
            message.from_user.id,
            message.text,
            '✅ Изображение установлено'
        )

        await message.answer(ADMIN_TITLE, reply_markup=ikb_admin)
        await OrderDB.set_url('main_image', message.text)
        await state.finish()
    except aiogram.utils.exceptions.BadRequest:

        await bot.send_message(
            message.from_user.id,
            'Неверная ссылка, изображение не найдено',
            reply_markup=ikb_cancel
        )

    await message.delete()


@dp.message_handler(state=OrderComment.get_comment)
async def set_comment(message: types.Message, state: FSMContext):
    """
    Order comment
    State of getting comment for order
    """
    await OrderDB.set_comment(message.from_user.id, message.text)
    await state.finish()
    await message.delete()

    await bot.send_message(
        chat_id=message.from_user.id,
        text=await basket_title(message.from_user.id),
        reply_markup=await pages.basket_menu_page(message.from_user.id)
    )


@dp.message_handler(state=Mail.new_mail)
async def get_mail_msg(message: types.Message, state: FSMContext):
    """
    Mail
    State of getting new mail
    """
    if len(message.text) > 5:
        await OrderDB.insert_mail(message.text)
        mail_id, mail_text = await OrderDB.get_mail()
        await state.finish()
        await message.answer(mail_text, reply_markup=await pages.my_mails(int(mail_id)))
    await message.delete()


@dp.message_handler()
async def message_filter(message: types.Message):
    """Handler of product name and other messages"""

    products = await OrderDB.get_prices()
    for product in products:
        if message.text == product[0]:
            try:
                await bot.send_photo(
                    message.from_user.id,
                    photo=product[3],
                    caption=f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                    reply_markup=await pages.product_page(message.from_user.id, product[0])
                )

            except aiogram.utils.exceptions.BadRequest:

                await bot.send_message(
                    message.from_user.id,
                    f'<b>{product[0]}</b>\nСостав: {product[2]}\nЦена: {product[1]}₽',
                    reply_markup=await pages.product_page(message.from_user.id, product[0])
                )

            await OrderDB.add_temp(message.from_user.id, product[0])
    await message.delete()


@dp.inline_handler(text='#menu')
async def inline_h(query: types.InlineQuery):
    if get_json('data.json')['is_bot_enabled']:
        item_list = []
        prices = await OrderDB.get_prices()

        for product in prices:
            product = list(product)
            if query.chat_type == 'sender':
                msg = InputTextMessageContent(product[0])
            else:
                msg = InputTextMessageContent(PRIVATE_MESSAGE)
            if product[2] is None:
                product[2] = ''
            item_list.append(InlineQueryResultArticle(
                id=await generate_id(),
                input_message_content=msg,
                title=product[0],
                thumb_url=product[3],
                description=f'Состав: {product[2]}\nЦена: {product[1]}₽')
            )

        await bot.answer_inline_query(query.id, item_list, cache_time=1)
    else:
        await bot.send_message(query.from_user.id, PAUSE_MESSAGE)


@dp.callback_query_handler(
    state=[Login.admin_password, Login.employee_password, ChangeProduct.get_new_desc,
           ChangeProduct.get_new_product_image, ChangeProduct.get_new_price,
           AddProduct.get_price, AddProduct.get_image, AddProduct.get_name, AddProduct.get_desc,
           ChangeMainImage.get_main_image, OrderComment.get_comment, ErrorHandler.get_error,
           Mail.new_mail]
)
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    """Add Cancel button for message"""
    await callbacks.cancel_callback(callback, bot, state, ProductList)


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    await callbacks.handler(callback.from_user.id, callback.message.message_id, callback, bot)


# PAYMENT
# =================================================================================================


@dp.pre_checkout_query_handler()
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    """Sending messages with order information to user and employee"""

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

    await bot.send_message(
        chat_id=message.from_user.id,
        text=msg
    )

    await OrderDB.clear_basket(message.from_user.id)

    if order_user_time is not None:
        result_time = order_user_time
        user_time_str = f'\n⏱ <b>Приготовить к {order_user_time}</b>\n'
    else:
        result_time = time
        user_time_str = ''

    await OrderDB.insert_to_archive(
        message.from_user.id, order_number, order_list, comment, price, result_time
    )

    print(
        {'user_id': message.from_user.id,
         'order_number': order_number,
         'order_list': order_list,
         'price': str(price) + cur,
         'order_user_time': order_user_time,
         'comment': comment,
         'date': date,
         'time': time
         }
    )

    await send_order_to_employees(
        comment, payload, bot, order_number, user_time_str, price, date, time
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
