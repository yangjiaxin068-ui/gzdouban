import pyodbc


SERVER = "localhost"
DATABASE = "gzdouban"


def _get_sql_server_driver():
    drivers = pyodbc.drivers()
    for driver in (
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server",
    ):
        if driver in drivers:
            return driver
    raise RuntimeError("No SQL Server ODBC driver found. Please install Microsoft ODBC Driver 17/18 for SQL Server.")


def get_conn():
    driver = _get_sql_server_driver()
    conn = pyodbc.connect(
        f"DRIVER={{{driver}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    cursor = conn.cursor()
    return conn, cursor
