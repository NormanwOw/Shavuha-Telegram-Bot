from order_db import OrderDB

MAIN_PAGE = '<b>За углом втихаря</b> 🌮\n\n   Рады приветствовать вас в нашем телеграм боте.\n' \
            'Здесь вы можете оформить заказ, оплатить его, и после чего мы сразу же приступим к ' \
            'его приготовлению. Забрать заказ вы можете по адресу г.Пермь, ул.Куйбышева 147/1. ' \
            '\n\n   По всем интересуюшим вас вопросам обращайтесь по телефону ' \
            '📞 <u>+7(952)664-17-06</u>.\n\nРаботаем круглосуточно без выходных'


async def basket_title(user_id: int) -> str:
    title = '🛒 <b>Корзина</b>'
    time = await OrderDB.get_order_user_time(user_id)
    comment = await OrderDB.get_comment(user_id)
    if time is None:
        time = ''
    else:
        time = '\n⏱ ' + await OrderDB.get_order_user_time(user_id)

    if comment is None:
        comment = ''
    else:
        comment = '\n✏ ' + comment

    return title + time + comment


async def order_comment_title(user_id: int) -> str:
    title = '<b>✏ Комментарий к заказу</b>'
    comment = await OrderDB.get_comment(user_id)
    if comment is None:
        comment = ''
    else:
        comment = '\n ' + comment
    return title + comment


ADMIN_TITLE = '🛠 <b>Панель управления</b>'


async def admin_stats() -> str:
    avg_price = await OrderDB.get_avg_order_price()
    orders_24h = await OrderDB.get_orders_count_24h()
    orders = await OrderDB.get_orders_count()
    return ADMIN_TITLE+f'\n ▫️ Заказы за 24 часа: {orders_24h}' \
                       f'\n ▫️ Всего заказов: {orders}' \
                       f'\n ▫️ Средний чек: {avg_price}'

STAFF_TITLE = '👬 <b>Персонал</b>'
SETTINGS_TITLE = '⚙ <b>Настройки</b>'
STAFF_MESSAGE = '✅ <b>Вход успешно выполнен</b>\n\nВсе заказы через систему бота будут приходить в этот чат'
EDIT_MENU_TITLE = '🍱 <b>Редактор меню</b>'

EMPTY_BASKET = '🛒 <b>Корзина пуста</b>'

SUCCESSFUL_MESSAGE = '<b>Заказ №<u>{order_number}</u></b>\n\n   Заказ на сумму <b>{amount}{cur}</b> ' \
                     'успешно оформлен ✅\n\n   Забрать его вы можете по адресу г.Пермь, ул.Куйбышева 147/1' \
                     ' в любое удобное для вас время. Работаем круглосуточно без выходных.\n\n<b>Ждём вас</b> 😊'

PRIVATE_MESSAGE = 'Вас приветствует бот кафе <b>🌮 За углом втихаря</b> г.Пермь\n' \
                  'У меня @za_uglom_bot вы можете оформить заказ из списка <b>#menu</b>'

SET_TIME_MESSAGE = '<b>⏱ Время</b>\n\n   Здесь вы можете уточнить время, к которому будет приготовлен заказ.\n' \
                   '   <b>Это необязательно</b>. Без установки времени после оплаты мы сразу приступим ' \
                   'к приготовлению 🌮'

MENU_HELP = '\n🚫 - удаление товара из базы данных\n🌆 - замена изображения\n₽ - изменение цены\n' \
            '[+] - Добавление нового товара в базу данных'
STAFF_HELP = '   Для подключения сотрудника к боту, сообщите ему <b>пароль для персонала</b>. Далее, ему ' \
             'необходимо ввести команду <b>/personal</b> на главной странице этого бота, после чего воспользоваться ' \
             '<b>паролем персонала</b>.\n   Подключенным к боту сотрудникам в личные сообщения будут приходить ' \
             'оплаченные посетителями заказы.\n   Список подключенных в данный момент сотрудников отображается ' \
             'ниже.\n🚫 - отключение сотрудника от бота'
