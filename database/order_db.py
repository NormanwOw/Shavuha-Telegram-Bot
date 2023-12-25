import json
import datetime

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from bot.config import DATABASE_URL
from bot.config import redis


class OrderDB:

    def __init__(self):
        self.__async_engine = create_async_engine(url=DATABASE_URL)
        self.redis = redis.client()

    # BASKETS TABLE ===============================================================================
    async def get_basket(self, user_id: int) -> dict or None:
        async with self.redis as conn:
            basket = await conn.get(f'basket_{user_id}')

            if basket is None:
                return None

            return json.loads(basket)

    async def set_basket(self, user_id: int, basket: dict):
        async with self.redis as conn:
            basket = json.dumps(basket, ensure_ascii=False)
            await conn.set(f'basket_{user_id}', basket)

    async def clear_basket(self, user_id: int):
        async with self.redis as conn:
            await conn.delete(f'basket_{user_id}')

    async def get_order_list(self, user_id: int) -> dict or None:
        basket = await self.get_basket(user_id)

        if basket is None:
            return None

        return basket['order_list']

    async def set_order_list(self, user_id: int, order_list: dict):
        basket = await self.get_basket(user_id)
        basket['order_list'] = order_list
        await self.set_basket(user_id, basket)

    async def add_order(self, user_id: int, new_order_list: dict):
        order_list = await self.get_order_list(user_id)

        if order_list is None:
            basket = {'order_list': new_order_list,
                      'price': 0,
                      'order_user_time': None,
                      'order_time': None,
                      'comment': None,
                      }
            await self.set_basket(user_id, basket)
        else:
            for item in new_order_list:
                if item in order_list:
                    count = new_order_list[item] + order_list[item]
                    if count == 0:
                        del order_list[item]
                    else:
                        order_list[item] = count

                else:
                    order_list = order_list | new_order_list

            await self.set_order_list(user_id, order_list)

        await self.update_price(user_id)

    async def get_basket_products_count(self, user_id: int) -> int:
        order_list = await self.get_order_list(user_id)
        if order_list is None:
            return 0

        count = sum([count for count in order_list.values()])

        return count

    async def set_price(self, user_id: int, price: int):
        basket = await self.get_basket(user_id)
        basket['price'] = price
        await self.set_basket(user_id, basket)

    async def get_price(self, user_id: int) -> int:
        basket = await self.get_basket(user_id)
        return basket['price']

    async def set_order_time(self, user_id: int, time: str):
        basket = await self.get_basket(user_id)
        basket['order_time'] = time
        await self.set_basket(user_id, basket)

    async def get_order_time(self, user_id: int) -> str:
        basket = await self.get_basket(user_id)
        return basket['order_time']

    async def set_order_user_time(self, user_id: int, time: str or None):
        basket = await self.get_basket(user_id)
        basket['order_user_time'] = time
        await self.set_basket(user_id, basket)

    async def get_order_user_time(self, user_id: int) -> str:
        basket = await self.get_basket(user_id)
        return basket['order_user_time']

    async def set_comment(self, user_id: int, comment: str):
        basket = await self.get_basket(user_id)
        basket['comment'] = comment
        await self.set_basket(user_id, basket)

    async def get_comment(self, user_id: int) -> str:
        basket = await self.get_basket(user_id)
        return basket['comment']

    async def delete_comment(self, user_id: int):
        basket = await self.get_basket(user_id)
        basket['comment'] = None
        await self.set_basket(user_id, basket)

    # PRICES TABLE
    # =============================================================================================
    async def add_product(self, product_list: list):
        async with self.__async_engine.connect() as connect:
            try:
                product, price, description, url = product_list
                stmt = text(
                    "INSERT INTO prices (product, price, description, url) "
                    "VALUES (:product, :price, :description, :url)"
                ).bindparams(product=product, price=price, description=description, url=url)

                await connect.execute(stmt)
                await connect.commit()

            except Exception:
                pass

    async def get_prices(self) -> list:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT product, price, description, url FROM prices ORDER BY id"
            )
            query = await connect.execute(query)

            return query.all()

    async def get_price_by_product_name(self, product: str) -> int:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT price FROM prices WHERE product=:product"
            ).bindparams(product=product)

            query = await connect.execute(query)

            return query.scalar()

    async def update_price(self, user_id: int):
        product_list = await self.get_prices()
        order = await self.get_order_list(user_id)

        total_price = 0
        for item in order:
            for price in product_list:
                if item == price[0]:
                    total_price += order[item] * price[1]

        await self.set_price(user_id, total_price)

    async def set_product_desc(self, description: str, product: str):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE prices SET description=:description WHERE product=:product"
            ).bindparams(description=description, product=product)

            await connect.execute(stmt)
            await connect.commit()

    async def set_product_image(self, url: str, product: str):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE prices SET url=:url WHERE product=:product"
            ).bindparams(url=url, product=product)

            await connect.execute(stmt)
            await connect.commit()

    async def set_product_price(self, price: int, product: str):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE prices SET price=:price WHERE product=:product"
            ).bindparams(price=price, product=product)

            await connect.execute(stmt)
            await connect.commit()

    async def delete_product(self, product: str):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "DELETE FROM prices WHERE product=:product"
            ).bindparams(product=product)

            await connect.execute(stmt)
            await connect.commit()

    # ORDERS TABLE
    # =============================================================================================

    async def insert_to_orders(
            self, user_id: int, order_number: int, order_list: str, comment: str, price: int,
            time: str
    ):
        date = datetime.datetime.now().strftime('%d.%m.%Y')

        async with self.__async_engine.connect() as connect:
            stmt = text(
                "INSERT INTO orders (order_number, user_id, order_list, "
                "comment, price, date, time) "
                "VALUES (:order_number, :user_id, :order_list, :comment, :price, "
                ":date, :time)"
            ).bindparams(order_number=order_number, user_id=user_id, order_list=order_list,
                         comment=comment, price=price, date=date, time=time)

            await connect.execute(stmt)
            await connect.commit()

    async def get_all_from_orders(self) -> list:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT * FROM orders"
            )
            query = await connect.execute(query)

            return list(query.all())

    async def get_order_numbers(self, order_number: int) -> int:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT order_number FROM orders WHERE order_number=:order_number"
            ).bindparams(order_number=order_number)

            query = await connect.execute(query)

            return query.scalar()

    async def get_avg_order_price(self) -> int:
        async with self.__async_engine.connect() as connect:
            try:
                query = text(
                    "SELECT AVG(price) FROM orders"
                )
                query = await connect.execute(query)

                return query.scalar()

            except TypeError:
                return 0

    async def get_orders(self, days: int) -> list:
        async with self.__async_engine.connect() as connect:
            date_class = datetime.datetime.now() + datetime.timedelta(hours=5)
            delta = datetime.timedelta(days=days)
            date_2_class = date_class - delta
            date = date_class.strftime('%d.%m.%Y')
            date_2 = date_2_class.strftime('%d.%m.%Y')

            if days == 1:
                query = text(
                    "SELECT order_number, price, order_list, comment, date, time "
                    "FROM orders WHERE date=:date OR date=:date_2"
                ).bindparams(date=date, date_2=date_2)

                query = await connect.execute(query)
                days_list = list(query.scalars().all())

                for day_time in days_list:
                    d = day_time[4]
                    t = day_time[5]
                    user_date = datetime.datetime(int(d[6:]), int(d[3:5]), int(d[0:2]),
                                                  hour=int(t[0:2]), minute=int(t[3:5]))
                    if user_date < date_2_class:
                        days_list.remove(day_time)
                return days_list

            elif days == 30:
                day_date = date[:2]
                date = date[2:]
                month_date2 = date_2[3:5]
                date_2 = date_2[2:]

                query = text(
                    f"SELECT order_number, price, order_list, comment, date, time "
                    f"FROM orders WHERE date LIKE :date "
                    f"OR date LIKE :date_2"
                ).bindparams(date=f'__{date}', date_2=f'__{date_2}', )

                query = await connect.execute(query)
                days_list = list(query.scalars().all())

                days_list_copy = days_list.copy()
                for day in days_list:
                    if int(day[4][0:2]) < int(day_date) and int(day[4][3:5]) == int(month_date2):
                        days_list_copy.remove(day)
                return days_list_copy

    async def get_orders_count_days(self, days: int) -> int:
        try:
            return len(await self.get_orders(days))
        except TypeError:
            return 0

    async def get_orders_count(self):
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT COUNT(*) FROM orders"
            )
            query = await connect.execute(query)

            return query.scalar()

    async def get_user_orders(self, user_id):
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT order_number, price, order_list, date, time FROM orders "
                "WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            query = await connect.execute(query)

            return query.all()

    async def get_all_user_id(self) -> list or False:
        async with self.__async_engine.connect() as connect:
            try:
                query = text(
                    "SELECT user_id FROM orders"
                )
                query = await connect.execute(query)
                result = set(query.scalars())

                return list(result)

            except TypeError:
                return False

    # EMPLOYEES TABLE
    # =============================================================================================

    async def add_employee(self, user_id: int, full_name: str, status: str):
        async with self.__async_engine.connect() as connect:
            date = datetime.datetime.now().strftime('%d.%m.%Y')

            stmt = text(
                "INSERT INTO employees (user_id, full_name, status, date) "
                "VALUES (:user_id, :full_name, :status, :date)"
            ).bindparams(user_id=user_id, full_name=full_name, status=status, date=date)

            await connect.execute(stmt)
            await connect.commit()

    async def get_id_by_status(self, status: str) -> list:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT user_id FROM employees WHERE status=:status"
            ).bindparams(status=status)

            query = await connect.execute(query)

            return query.scalars()

    async def get_id_name_by_status(self, status: str) -> list:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT user_id, full_name FROM employees WHERE status=:status"
            ).bindparams(status=status)

            query = await connect.execute(query)

            result = []
            for employee in query:
                name = employee[1]
                if ' ' in name:
                    name = name.split()[0]
                result.append((employee[0], name))

            return result

    async def delete_employee(self, user_id: int):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "DELETE FROM employees WHERE user_id=:user_id AND status='Повар'"
            ).bindparams(user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    # TEMP TABLE
    # =============================================================================================

    async def from_temp_to_basket(self, user_id: int):
        order_list = await self.get_order(user_id)
        await self.add_order(user_id, order_list)

    async def delete_temp(self, user_id: int):
        async with self.redis as conn:
            await conn.delete(str(user_id))

    async def update_temp(self, user_id: int, product: str, count: int) -> int:
        async with self.redis as conn:
            count_product = 1
            order_list = await conn.get(str(user_id))

            if order_list is None:
                order_list = json.dumps({product: count_product}, ensure_ascii=False)
                await conn.set(str(user_id), order_list)
            else:
                order_list = json.loads(order_list)
                for item in order_list.keys():
                    if item == product:
                        order_list[item] += count
                        count_product = order_list[item]
                order_list = json.dumps(order_list, ensure_ascii=False)

                if count_product > 0:
                    await conn.set(str(user_id), order_list)

            return count_product

    async def get_order(self, user_id: int) -> dict or None:
        async with self.redis as conn:
            order = await conn.get(str(user_id))

            if order is None:
                return None

            return json.loads(order)

    async def get_temp_products_count(self, user_id: int) -> int or 0:
        try:
            order_list = await self.get_order(user_id)
            count = 0

            for product in order_list:
                count += order_list[product]

            return count

        except TypeError:
            return 0

    async def get_count(self, user_id: int) -> int:
        order_list = await self.get_order(user_id)

        if order_list is None:
            return 0

        order_list = json.loads(order_list)
        count = sum([count for count in order_list.values()])

        return count

    async def get_count_by_product(self, user_id: int, product: str) -> int:
        order = await self.get_order(user_id)
        if order is None:
            return 1

        return order.get(product, 1)

    # URLS TABLE
    # =============================================================================================

    async def set_url(self, title: str, url: str):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE urls SET url=:url WHERE title=:title"
            ).bindparams(url=url, title=title)

            await connect.execute(stmt)
            await connect.commit()

    async def get_url(self, title: str) -> str:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT url FROM urls WHERE title=:title"
            ).bindparams(title=title)

            query = await connect.execute(query)

            return query.scalar()

    # PRICES TABLE
    # =============================================================================================
    async def insert_error(self, username: int, error: str, date: str, time: str):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "INSERT INTO errors (username, error, date, time) "
                "VALUES (:username, :error, :date, :time)"
            ).bindparams(username=username, error=error, date=date, time=time)

            await connect.execute(stmt)
            await connect.commit()

    # MAILS TABLE
    # =============================================================================================

    async def insert_mail(self, mail: str):
        async with self.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE mails SET selected=false"
            )
            await connect.execute(stmt)

            mail_id = await self.get_mails_count() + 1

            stmt = text(
                "INSERT INTO mails (id, mail, selected) VALUES (:id, :mail, true)"
            ).bindparams(id=mail_id, mail=mail)
            await connect.execute(stmt)

            await connect.commit()

    async def get_mail(self) -> tuple:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT (id, mail) FROM mails WHERE selected=true"
            )
            query = await connect.execute(query)

            return query.scalar()

    async def get_mails_count(self) -> int:
        async with self.__async_engine.connect() as connect:
            query = text(
                "SELECT COUNT(mail) FROM mails"
            )
            query = await connect.execute(query)

            return query.scalar()

    async def delete_mail(self):
        async with self.__async_engine.connect() as connect:
            mail = await self.get_mail()
            stmt = text(
                "DELETE FROM mails WHERE selected=true"
            )
            await connect.execute(stmt)
            await connect.commit()

            mails_count = await self.get_mails_count()
            selected_id = count = mail[0]
            for _ in range(mails_count + 1 - selected_id):
                stmt = text(
                    "UPDATE mails SET id=:id WHERE id=:id_up"
                ).bindparams(id=count, id_up=count + 1)

                count += 1
                await connect.execute(stmt)

            await connect.commit()

            try:
                query = text(
                    "SELECT id FROM mails ORDER BY id DESC LIMIT 1"
                )
                query = await connect.execute(query)
                mail_id = query.scalar()

                stmt = text(
                    "UPDATE mails SET selected=true WHERE id=:id"
                ).bindparams(id=mail_id)

                await connect.execute(stmt)
                await connect.commit()

            except TypeError:
                return False

    async def move_selected_mail(self, direct: bool):
        async with self.__async_engine.connect() as connect:
            move = 1 if direct else -1
            query = text(
                "SELECT id FROM mails WHERE selected=true"
            )
            query = await connect.execute(query)
            mail_id = query.scalar()

            stmt = text(
                "UPDATE mails SET selected=false"
            )
            await connect.execute(stmt)

            stmt = text(
                "UPDATE mails SET selected=true WHERE id=:id"
            ).bindparams(id=mail_id + move)

            await connect.execute(stmt)
            await connect.commit()


database = OrderDB()
