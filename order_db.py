import json
import datetime

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import DATABASE_URL


class OrderDB:
    __async_engine = create_async_engine(url=DATABASE_URL)

    # BASKETS TABLE ===============================================================================
    @classmethod
    async def get_order_list(cls, user_id: int) -> dict or None:
        async with cls.__async_engine.connect() as connect:
            try:
                query = text(
                    "SELECT order_list FROM baskets WHERE user_id=:user_id"
                ).bindparams(user_id=user_id)

                order = await connect.execute(query)

                return json.loads(order.scalar())

            except TypeError:
                return None

    @classmethod
    async def get_order_by_id(cls, user_id: int) -> list or None:
        async with cls.__async_engine.connect() as connect:
            try:
                query = text(
                    "SELECT * FROM baskets WHERE user_id=:user_id"
                ).bindparams(user_id=user_id)

                order = await connect.execute(query)

                return [x for x in order.fetchone()]

            except TypeError:
                return None

    @classmethod
    async def add_order(cls, user_id: int, new_order_list: dict):
        async with cls.__async_engine.connect() as connect:
            order_list = await cls.get_order_list(user_id)

            if order_list is None:
                new_order_list_js = json.dumps(new_order_list, ensure_ascii=False)

                stmt = text(
                    "INSERT INTO baskets (user_id, order_list) VALUES (:user_id, :order_list)"
                ).bindparams(user_id=user_id, order_list=new_order_list_js)

                await connect.execute(stmt)
                await connect.commit()
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

                order_list = json.dumps(order_list, ensure_ascii=False)

                stmt = text(
                    "UPDATE baskets SET order_list=:order_list WHERE user_id=:user_id"
                ).bindparams(order_list=order_list, user_id=user_id)

                await connect.execute(stmt)
                await connect.commit()

            await cls.update_price(user_id)

    @classmethod
    async def get_basket_products_count(cls, user_id: int) -> int:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_list FROM baskets WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            query = await connect.execute(query)
            query = query.scalar()
            if query is None:
                return 0

            order_list = json.loads(query)
            count = sum([count for count in order_list.values()])

            return count

    @classmethod
    async def set_price(cls, user_id: int, price: int):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE baskets SET price=:price WHERE user_id=:user_id"
            ).bindparams(price=price, user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def get_price(cls, user_id: int) -> int:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT price FROM baskets WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            price = await connect.execute(query)

            return price.scalar()

    @classmethod
    async def set_order_time(cls, user_id: int, time: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE baskets SET order_time=:time WHERE user_id=:user_id"
            ).bindparams(time=time, user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def get_order_time(cls, user_id: int) -> str:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_time FROM baskets WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def set_order_user_time(cls, user_id: int, time: str or None):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE baskets SET order_user_time=:time WHERE user_id=:user_id"
            ).bindparams(time=time, user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def get_order_user_time(cls, user_id: int) -> str:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_user_time FROM baskets WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def clear_basket(cls, user_id: int):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "DELETE FROM baskets WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def set_comment(cls, user_id: int, comment: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE baskets SET comment=:comment WHERE user_id=:user_id"
            ).bindparams(comment=comment, user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def get_comment(cls, user_id: int) -> str:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT comment FROM baskets WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def delete_comment(cls, user_id: int):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE baskets SET comment=NULL WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    # PRICES TABLE
    # =============================================================================================
    @classmethod
    async def add_product(cls, product_list: list):
        async with cls.__async_engine.connect() as connect:
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

    @classmethod
    async def get_prices(cls) -> list:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT (product, price, description, url) FROM prices ORDER BY id"
            )
            query = await connect.execute(query)

            return query.scalars().all()

    @classmethod
    async def get_price_by_product_name(cls, product: str) -> int:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT price FROM prices WHERE product=:product"
            ).bindparams(product=product)

            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def update_price(cls, user_id: int):
        product_list = await cls.get_prices()
        order = await cls.get_order_list(user_id)

        total_price = 0
        for item in order:
            for price in product_list:
                if item == price[0]:
                    total_price += order[item] * price[1]

        await cls.set_price(user_id, total_price)

    @classmethod
    async def set_product_desc(cls, description: str, product: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE prices SET description=:description WHERE product=:product"
            ).bindparams(description=description, product=product)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def set_product_image(cls, url: str, product: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE prices SET url=:url WHERE product=:product"
            ).bindparams(url=url, product=product)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def set_product_price(cls, price: int, product: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE prices SET price=:price WHERE product=:product"
            ).bindparams(price=price, product=product)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def delete_product(cls, product: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "DELETE FROM prices WHERE product=:product"
            ).bindparams(product=product)

            await connect.execute(stmt)
            await connect.commit()

    # ARCHIVE TABLE
    # =============================================================================================

    @classmethod
    async def insert_to_archive(cls, user_id: int, order_number: int, order_list: str,
                                comment: str, price: int, time: str):
        date = datetime.datetime.now().strftime('%d.%m.%Y')

        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "INSERT INTO archive (order_number, user_id, order_list, "
                "comment, price, date, time) "
                "VALUES (:order_number, :user_id, :order_list, :comment, :price, "
                ":date, :time)"
            ).bindparams(order_number=order_number, user_id=user_id, order_list=order_list,
                         comment=comment, price=price, date=date, time=time)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def get_all_from_archive(cls):
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT * FROM archive"
            )
            query = await connect.execute(query)

            return query.all()

    @classmethod
    async def get_order_numbers(cls, order_number: int) -> int:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_number FROM archive WHERE order_number=:order_number"
            ).bindparams(order_number=order_number)

            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def get_avg_order_price(cls) -> int:
        async with cls.__async_engine.connect() as connect:
            try:
                query = text(
                    "SELECT AVG(price) FROM archive"
                )
                query = await connect.execute(query)

                return query.scalar()

            except TypeError:
                return 0

    @classmethod
    async def get_orders(cls, days: int) -> list:
        async with cls.__async_engine.connect() as connect:
            date_class = datetime.datetime.now() + datetime.timedelta(hours=5)
            delta = datetime.timedelta(days=days)
            date_2_class = date_class - delta
            date = date_class.strftime('%d.%m.%Y')
            date_2 = date_2_class.strftime('%d.%m.%Y')

            if days == 1:
                query = text(
                    "SELECT order_number, price, order_list, comment, date, time "
                    "FROM archive WHERE date=:date OR date=:date_2"
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
                    f"FROM archive WHERE date LIKE :date "
                    f"OR date LIKE :date_2"
                ).bindparams(date=f'__{date}', date_2=f'__{date_2}', )

                query = await connect.execute(query)
                days_list = list(query.scalars().all())

                days_list_copy = days_list.copy()
                for day in days_list:
                    if int(day[4][0:2]) < int(day_date) and int(day[4][3:5]) == int(month_date2):
                        days_list_copy.remove(day)
                return days_list_copy

    @classmethod
    async def get_orders_count_day(cls) -> int:
        try:
            return len(await cls.get_orders(1))
        except TypeError:
            return 0

    @classmethod
    async def get_orders_count_month(cls) -> int:
        try:
            return len(await cls.get_orders(30))
        except TypeError:
            return 0

    @classmethod
    async def get_orders_count(cls):
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT COUNT(*) FROM archive"
            )
            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def get_user_orders(cls, user_id):
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_number, price, order_list, date, time FROM archive "
                "WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            query = await connect.execute(query)

            return query.all()

    @classmethod
    async def get_all_user_id(cls) -> list or False:
        async with cls.__async_engine.connect() as connect:
            try:
                query = text(
                    "SELECT user_id FROM archive"
                )
                query = await connect.execute(query)
                result = set(query.scalars())

                return list(result)

            except TypeError:
                return False

    # EMPLOYEES TABLE
    # =============================================================================================

    @classmethod
    async def add_employee(cls, user_id: int, full_name: str, status: str):
        async with cls.__async_engine.connect() as connect:
            date = datetime.datetime.now().strftime('%d.%m.%Y')

            stmt = text(
                "INSERT INTO employees (user_id, full_name, status, date) "
                "VALUES (:user_id, :full_name, :status, :date)"
            ).bindparams(user_id=user_id, full_name=full_name, status=status, date=date)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def get_id_by_status(cls, status: str) -> list:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT user_id FROM employees WHERE status=:status"
            ).bindparams(status=status)

            query = await connect.execute(query)

            return query.scalars()

    @classmethod
    async def get_id_name_by_status(cls, status: str) -> list:
        async with cls.__async_engine.connect() as connect:
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

    @classmethod
    async def delete_employee(cls, user_id: int):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "DELETE FROM employees WHERE user_id=:user_id AND status='Повар'"
            ).bindparams(user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    # TEMP TABLE
    # =============================================================================================

    @classmethod
    async def from_temp_to_basket(cls, user_id: int):
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_list FROM temp WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            order = await connect.execute(query)
            order = order.scalar()

            await cls.add_order(user_id, json.loads(order))

    @classmethod
    async def delete_temp(cls, user_id: int):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "DELETE FROM temp WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def update_temp(cls, user_id: str, product: str, count: int) -> int:
        async with cls.__async_engine.connect() as connect:
            count_product = 1

            query = text(
                "SELECT order_list FROM temp WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            order = await connect.execute(query)
            order_list = order.scalar()

            if order_list is None:
                order_list = json.dumps({product: count_product}, ensure_ascii=False)
                stmt = text(
                    "INSERT INTO temp (user_id, order_list) "
                    "VALUES (:user_id, :order_list)"
                ).bindparams(user_id=user_id, order_list=order_list)
                await connect.execute(stmt)
                await connect.commit()
            else:
                order_list = json.loads(order_list)
                for item in order_list.keys():
                    if item == product:
                        order_list[item] += count
                        count_product = order_list[item]
                order_list = json.dumps(order_list, ensure_ascii=False)

                if count_product > 0:
                    stmt = text(
                        "UPDATE temp SET order_list=:order_list WHERE user_id=:user_id"
                    ).bindparams(order_list=order_list, user_id=user_id)

                    await connect.execute(stmt)
                    await connect.commit()

        return count_product

    @classmethod
    async def get_order(cls, user_id: int) -> dict or None:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_list FROM temp WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            order = await connect.execute(query)
            order = order.scalar()

            if order is None:
                return order

            return json.loads(order)

    @classmethod
    async def get_temp_products_count(cls, user_id: int) -> int or 0:
        async with cls.__async_engine.connect() as connect:
            try:
                query = text(
                    "SELECT order_list FROM temp WHERE user_id=:user_id"
                ).bindparams(user_id=user_id)

                order = await connect.execute(query)
                order = json.loads(order.scalar())

                count = 0
                for product in order:
                    count += order[product]

                return count

            except TypeError:
                return 0

    @classmethod
    async def get_count(cls, user_id: int) -> int:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT order_list FROM temp WHERE user_id=:user_id"
            ).bindparams(user_id=user_id)

            query = await connect.execute(query)
            order_list = query.scalar()

            if order_list is None:
                return 0

            order_list = json.loads(order_list)

            count = sum([count for count in order_list.values()])

            return count

    @classmethod
    async def get_count_by_product(cls, user_id: int, product: str) -> int:
        order = await cls.get_order(user_id)
        try:
            if order is None:
                return 1

            return order[product]
        except KeyError:
            return 1

    # URLS TABLE
    # =============================================================================================

    @classmethod
    async def set_url(cls, title: str, url: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE urls SET url=:url WHERE title=:title"
            ).bindparams(url=url, title=title)

            await connect.execute(stmt)
            await connect.commit()

    @classmethod
    async def get_url(cls, title: str) -> str:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT url FROM urls WHERE title=:title"
            ).bindparams(title=title)

            query = await connect.execute(query)

            return query.scalar()

    # PRICES TABLE
    # =============================================================================================
    @classmethod
    async def insert_error(cls, username: int, error: str, date: str, time: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "INSERT INTO errors (username, error, date, time) "
                "VALUES (:username, :error, :date, :time)"
            ).bindparams(username=username, error=error, date=date, time=time)

            await connect.execute(stmt)
            await connect.commit()

    # MAILS TABLE
    # =============================================================================================

    @classmethod
    async def insert_mail(cls, mail: str):
        async with cls.__async_engine.connect() as connect:
            stmt = text(
                "UPDATE mails SET selected=false"
            )
            await connect.execute(stmt)

            mail_id = await cls.get_mails_count() + 1

            stmt = text(
                "INSERT INTO mails (id, mail, selected) VALUES (:id, :mail, true)"
            ).bindparams(id=mail_id, mail=mail)
            await connect.execute(stmt)

            await connect.commit()

    @classmethod
    async def get_mail(cls) -> tuple:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT (id, mail) FROM mails WHERE selected=true"
            )
            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def get_mails_count(cls) -> int:
        async with cls.__async_engine.connect() as connect:
            query = text(
                "SELECT COUNT(mail) FROM mails"
            )
            query = await connect.execute(query)

            return query.scalar()

    @classmethod
    async def delete_mail(cls):
        async with cls.__async_engine.connect() as connect:
            mail = await cls.get_mail()
            stmt = text(
                "DELETE FROM mails WHERE selected=true"
            )
            await connect.execute(stmt)
            await connect.commit()

            mails_count = await cls.get_mails_count()
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

    @classmethod
    async def move_selected_mail(cls, direct: bool):
        async with cls.__async_engine.connect() as connect:
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
