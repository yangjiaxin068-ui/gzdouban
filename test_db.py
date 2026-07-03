# -*- coding: utf-8 -*-
from tools.getDataBase import get_conn


def test():
    conn, cursor = get_conn()
    try:
        cursor.execute("SELECT DB_NAME()")
        result = cursor.fetchone()
        print("当前连接的数据库是：", result[0])
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    test()
