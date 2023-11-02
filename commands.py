from callbacks import *
from states import *


async def start_command(bot: Bot, message: types.Message):
    state = get_json('data.json')['is_bot_enabled']
    if state:
        await bot.send_photo(message.from_user.id,
                             await OrderDB.get_url('main_image'),
                             caption=MAIN_PAGE, reply_markup=ikb)
        await OrderDB.clear_basket(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, PAUSE_MESSAGE)

    await OrderDB.delete_temp(message.from_user.id)
    await message.delete()


async def admin_login(message: types.Message):
    adm_list = await OrderDB.get_id_by_status('Admin')
    if message.from_user.id in adm_list:
        await message.answer(ADMIN_TITLE, reply_markup=ikb_admin)
    else:
        await Logging.admin_password.set()
        await message.answer('Введите пароль:', reply_markup=ikb_cancel)
    await message.delete()


async def get_error_msg(message: types.Message):
    await message.answer(ERROR_TITLE, reply_markup=ikb_cancel)
    await message.delete()
    await ErrorHandler.get_error.set()
