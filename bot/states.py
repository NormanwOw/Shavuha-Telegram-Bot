from aiogram.dispatcher.filters.state import State, StatesGroup


class Login(StatesGroup):
    admin_password = State()
    employee_password = State()


class ChangeProduct(StatesGroup):
    get_new_desc = State()
    get_new_price = State()
    get_new_product_image = State()
    product = ''

    @classmethod
    async def set_product(cls, product):
        cls.product = product

    @classmethod
    async def get_product(cls):
        return cls.product


class ChangeMainImage(StatesGroup):
    get_main_image = State()


class AddProduct(StatesGroup):
    get_name = State()
    get_price = State()
    get_desc = State()
    get_image = State()


class OrderComment(StatesGroup):
    get_comment = State()


class ErrorHandler(StatesGroup):
    get_error = State()


class StateMail(StatesGroup):
    new_mail = State()
