from abc import ABC, abstractmethod
from database.order_db import database


class Menu(ABC):

    db = database

    @abstractmethod
    async def get_page(self, *args):
        pass

    @abstractmethod
    async def show_page(self, *args):
        pass
