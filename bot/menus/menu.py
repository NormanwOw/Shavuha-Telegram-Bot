from abc import ABC, abstractmethod
from database.order_db import OrderDB


class Menu(ABC):
    db = OrderDB

    @classmethod
    @abstractmethod
    async def get_page(cls, *args):
        pass

    @classmethod
    @abstractmethod
    async def show_page(cls, *args):
        pass
