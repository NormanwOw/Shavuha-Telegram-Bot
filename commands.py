from callbacks import *
from states import *


async def start_command(bot: Bot, message: types.Message):
    state = get_json('data.json')['state']
    if state:
        await bot.send_photo(message.from_user.id,
                             await OrderDB.get_url('main_image'),
                             caption=MAIN_PAGE, reply_markup=ikb)
        await OrderDB.clear_basket(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, PAUSE_MESSAGE)
    await message.delete()


async def admin_login(message: types.Message):
    adm_list = await OrderDB.get_id_by_status('Admin')
    if message.from_user.id in adm_list:
        await message.answer(ADMIN_TITLE, reply_markup=ikb_admin)
    else:
        await Logging.admin_password.set()
        await message.answer('Введите пароль:', reply_markup=ikb_cancel)
    await message.delete()


async def my_orders(message: types.Message):
    answer = ''
    title = ''
    user_orders = await OrderDB.get_user_orders(message.from_user.id)
    if len(user_orders) == 10:
        title = '<b>Последние 10 заказов</b>\n\n'
    elif len(user_orders) == 0:
        title = 'Список заказов пуст'
    for order_number, price, order_list, date, time in user_orders:
        answer += f'<b>Заказ №<u>{order_number}</u></b>\n{order_list}- Оплата: {int(price)}₽\n[{date} {time}]\n\n'
    await message.answer(title + answer)
    await message.delete()


async def admin_backup(message: types.Message):
    adm_list = await OrderDB.get_id_by_status('Admin')
    await message.delete()
    if message.from_user.id in adm_list:
        ya_disk.download('/database.db', 'database.db')


async def get_error_msg(message: types.Message):
    await message.answer(ERROR_TITLE, reply_markup=ikb_cancel)
    await message.delete()
    await ErrorHandler.get_error.set()