from bot.states import *
from bot.markups import *
from bot.callbacks import *
from bot.menus.admin import admin


async def start_command(bot: Bot, message: types.Message):
    state = await get_json()
    state = state['is_bot_enabled']

    if state:
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=await database.get_url('main_image'),
            caption=MAIN_PAGE, reply_markup=ikb_main
        )

        await database.clear_basket(message.from_user.id)
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=PAUSE_MESSAGE
        )

    await database.delete_temp(message.from_user.id)
    await message.delete()


async def admin_login(message: types.Message):
    adm_list = await database.get_id_by_status('Admin')
    if message.from_user.id in adm_list:
        await message.answer(ADMIN_TITLE, reply_markup=await admin.get_page())
    else:
        await Login.admin_password.set()
        await message.answer('Введите пароль:', reply_markup=ikb_cancel)
    await message.delete()


async def get_error_msg(message: types.Message):
    await message.answer(ERROR_TITLE, reply_markup=ikb_cancel)
    await message.delete()
    await ErrorHandler.get_error.set()
