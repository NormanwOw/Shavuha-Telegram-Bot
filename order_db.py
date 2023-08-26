import sqlite3
import json
import datetime


class OrderDB:
    __connection = sqlite3.connect('database.db')
    __cursor = __connection.cursor()

# ORDERS TABLE
    @classmethod
    async def get_order_list(cls, user_id) -> dict or None:
        with cls.__connection:
            try:
                order = cls.__cursor.execute("SELECT order_list FROM orders WHERE user_id = ?",
                                             (user_id,)).fetchone()[0]
                return json.loads(order)
            except TypeError:
                return None

    @classmethod
    async def get_order_by_id(cls, user_id: int) -> list or None:
        with cls.__connection:
            try:
                order = cls.__cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,)).fetchone()
                return [x for x in order]
            except TypeError:
                return None

    @classmethod
    async def get_products_count(cls, user_id: int) -> int or None:
        with cls.__connection:
            try:
                order = cls.__cursor.execute("SELECT order_list FROM orders WHERE user_id = ?",
                                             (user_id,)).fetchone()[0]
                order = json.loads(order)
                count = 0
                for product in order:
                    count += order[product]
                return count
            except TypeError:
                return 0

    @classmethod
    async def get_all_user_id(cls) -> list or None:
        with cls.__connection:
            try:
                users = cls.__cursor.execute("SELECT user_id FROM orders").fetchall()
                return [user[0] for user in users]
            except TypeError:
                return None

    @classmethod
    async def add_order(cls, user_id: int, new_order_list: dict):
        order_list = await OrderDB.get_order_list(user_id)
        if order_list is None:
            new_order_list = json.dumps(new_order_list, ensure_ascii=False)
            with cls.__connection:
                cls.__cursor.execute("INSERT INTO orders (user_id, order_list) VALUES (?, ?)",
                                     (user_id, new_order_list,))
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
            with cls.__connection:
                cls.__cursor.execute("UPDATE orders SET order_list = ? WHERE user_id = ?", (order_list, user_id,))

        await OrderDB.update_price(user_id)

    @classmethod
    async def set_price(cls, user_id: int, price: int):
        with cls.__connection:
            cls.__cursor.execute("UPDATE orders SET price = ? WHERE user_id = ?", (price, user_id,))

    @classmethod
    async def get_price(cls, user_id: int) -> int:
        with cls.__connection:
            return cls.__cursor.execute("SELECT price FROM orders WHERE user_id = ?", (user_id,)).fetchone()[0]

    @classmethod
    async def set_order_time(cls, user_id: int, time: str):
        with cls.__connection:
            cls.__cursor.execute("UPDATE orders SET order_time = ? WHERE user_id = ?", (time, user_id,))

    @classmethod
    async def get_order_time(cls, user_id: int) -> str:
        with cls.__connection:
            return cls.__cursor.execute("SELECT order_time FROM orders WHERE user_id = ?", (user_id,)).fetchone()[0]

    @classmethod
    async def set_order_user_time(cls, user_id: int, time: str or None):
        with cls.__connection:
            cls.__cursor.execute("UPDATE orders SET order_user_time = ? WHERE user_id = ?", (time, user_id,))

    @classmethod
    async def get_order_user_time(cls, user_id: int) -> str:
        with cls.__connection:
            return cls.__cursor.execute("SELECT order_user_time FROM orders WHERE user_id = ?",
                                        (user_id,)).fetchone()[0]

    @classmethod
    async def clear_basket(cls, user_id: int):
        with cls.__connection:
            cls.__cursor.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))

    @classmethod
    async def set_comment(cls, user_id: int, comment: str):
        with cls.__connection:
            cls.__cursor.execute("UPDATE orders SET comment = ? WHERE user_id = ?", (comment, user_id,))

    @classmethod
    async def get_comment(cls, user_id: int):
        with cls.__connection:
            return cls.__cursor.execute("SELECT comment FROM orders WHERE user_id = ?", (user_id,)).fetchone()[0]

    @classmethod
    async def delete_comment(cls, user_id: int):
        with cls.__connection:
            cls.__cursor.execute("UPDATE orders SET comment = NULL WHERE user_id = ?", (user_id,))

# PRICES TABLE
# ======================================================================================================================
    @classmethod
    async def add_product(cls, product: str, price: int, url: str or None):
        with cls.__connection:
            cls.__cursor.execute("INSERT INTO prices (product, price, url) VALUES (?, ?, ?)", (product, price, url,))

    @classmethod
    async def get_prices(cls) -> list:
        with cls.__connection:
            return cls.__cursor.execute("SELECT product, price, url FROM prices").fetchall()

    @classmethod
    async def get_price_by_product_name(cls, product: str) -> int:
        with cls.__connection:
            return cls.__cursor.execute("SELECT price FROM prices WHERE product = ?", (product,)).fetchone()[0]

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
    async def set_image(cls, url: str, product):
        with cls.__connection:
            cls.__cursor.execute("UPDATE prices SET url = ? WHERE product =?", (url, product,))

    @classmethod
    async def set_product_price(cls, product: str, price: int):
        with cls.__connection:
            cls.__cursor.execute("UPDATE prices SET price = ? WHERE product = ?", (price, product,))

    @classmethod
    async def delete_product(cls, product: str):
        with cls.__connection:
            cls.__cursor.execute("DELETE FROM prices WHERE product = ?", (product,))

# ARCHIVE TABLE
# ======================================================================================================================

    @classmethod
    async def add_to_archive(cls, user_id: int, order_number: int, order_list: str, comment: str, price: int, time: str):
        with cls.__connection:
            cls.__cursor.execute("INSERT INTO archive (order_number, user_id, order_list, comment, price, date, time) "
                                 "VALUES (?, ?, ?, ?, ?, strftime('%d.%m.%Y', date('now')), ?)",
                                 (order_number, user_id, order_list, comment, price, time))

    @classmethod
    async def get_order_numbers(cls) -> list:
        with cls.__connection:
            return [i[0] for i in cls.__cursor.execute("SELECT order_number FROM archive").fetchall()]

    @classmethod
    async def get_avg_order_price(cls) -> int:
        with cls.__connection:
            try:
                return int(cls.__cursor.execute("SELECT AVG(price) FROM archive").fetchone()[0])
            except TypeError:
                return 0

    @classmethod
    async def get_orders_24h(cls) -> list:
        date_class = datetime.datetime.now()
        delta = datetime.timedelta(days=1)
        date_2_class = date_class - delta
        date = date_class.strftime('%d.%m.%Y')
        date_2 = date_2_class.strftime('%d.%m.%Y')
        with cls.__connection:
            days_list = cls.__cursor.execute("SELECT order_number, price, order_list, comment, date, time FROM archive "
                                             "WHERE date = ? OR date = ?", (date, date_2)).fetchall()
            for day_time in days_list:
                d = day_time[4]
                t = day_time[5]
                user_date = datetime.datetime(int(d[6:]), int(d[3:5]), int(d[0:2]),
                                              hour=int(t[0:2]), minute=int(t[3:5]))
                if user_date < date_2_class:
                    days_list.remove(day_time)
            return days_list

    @classmethod
    async def get_orders_count_24h(cls) -> int:
        return len(await cls.get_orders_24h())

    @classmethod
    async def get_orders_count(cls):
        with cls.__connection:
            return cls.__cursor.execute("SELECT COUNT(*) FROM archive").fetchone()[0]

    @classmethod
    async def get_user_orders(cls, user_id):
        with cls.__connection:
            result = cls.__cursor.execute("SELECT order_number, price, order_list, "
                                          "date, time FROM archive WHERE user_id = ?", (user_id,)).fetchall()
            if len(result) > 10:
                result = result[-10:]
            return result

# EMPLOYEES TABLE
# ======================================================================================================================

    @classmethod
    async def add_employee(cls, user_id: int, full_name: str, status: str):
        with cls.__connection:
            cls.__cursor.execute("INSERT INTO employees (user_id, full_name, status, date) "
                                 "VALUES (?, ?, ?, strftime('%d.%m.%Y', date('now')))",
                                 (user_id, full_name, status,))

    @classmethod
    async def get_id_by_status(cls, status: str) -> list:
        with cls.__connection:
            return [user_id[0] for user_id in cls.__cursor.execute("SELECT user_id FROM employees WHERE status = ?",
                                                                   (status,)).fetchall()]

    @classmethod
    async def get_id_name_by_status(cls, status: str) -> list:
        with cls.__connection:
            employee_list = cls.__cursor.execute("SELECT user_id, full_name FROM employees "
                                                 "WHERE status = ?", (status,)).fetchall()
            result = []

            for employee in employee_list:
                name = employee[1]
                if ' ' in name:
                    name = name.split()[0]
                result.append((employee[0], name))

            return result

    @classmethod
    async def delete_employee(cls, user_id: int):
        with cls.__connection:
            cls.__cursor.execute("DELETE FROM employees WHERE user_id = ? AND status = 'Повар'", (user_id,))

# TEMP TABLE
# ======================================================================================================================

    @classmethod
    async def delete_temp(cls, user_id: int):
        with cls.__connection:
            cls.__cursor.execute("DELETE FROM temp WHERE user_id = ?", (user_id,))

    @classmethod
    async def add_temp(cls, user_id: int, product: str, count=1):
        with cls.__connection:
            cls.__cursor.execute("INSERT INTO temp (user_id, product, count) VALUES (?, ?, ?)",
                                 (user_id, product, count,))

    @classmethod
    async def temp_to_order(cls, user_id: int):
        with cls.__connection:
            temp = cls.__cursor.execute("SELECT * FROM temp WHERE user_id = ?", (user_id,)).fetchone()
            order_list = {temp[1]: temp[2]}
            await OrderDB.add_order(user_id, order_list)

    @classmethod
    async def set_count(cls, user_id: int, count=1):
        with cls.__connection:
            cls.__cursor.execute("UPDATE temp SET count = ? WHERE user_id = ?", (count, user_id,))

    @classmethod
    async def get_count(cls, user_id: int) -> int:
        with cls.__connection:
            try:
                count = cls.__cursor.execute("SELECT count FROM temp WHERE user_id = ?", (user_id,)).fetchone()[0]
                return count
            except TypeError:
                return 1

    @classmethod
    async def is_temp_exists(cls, user_id: int) -> bool:
        with cls.__connection:
            try:
                count = cls.__cursor.execute("SELECT count FROM temp WHERE user_id = ?", (user_id,)).fetchone()[0]
                return count
            except TypeError:
                return False

# URLS TABLE
# ======================================================================================================================
    @classmethod
    async def set_url(cls, title: str, url: str):
        with cls.__connection:
            cls.__cursor.execute("UPDATE urls SET url = ? WHERE title = ?", (url, title,))

    @classmethod
    async def get_url(cls, title: str) -> str:
        with cls.__connection:
            return cls.__cursor.execute("SELECT url FROM urls WHERE title = ?", (title,)).fetchone()[0]
