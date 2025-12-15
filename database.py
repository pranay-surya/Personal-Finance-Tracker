import pymysql

# ================= DATABASE CONFIG =================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "expense_tracker"


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# ================= INSERT TRANSACTION =================
def add_transaction(trans_date, trans_type, category, amount, description):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO transactions (date, type, category, amount, description)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (trans_date, trans_type, category, amount, description))
        conn.commit()
    except pymysql.Error as e:
        raise Exception(f"Database Error: {e}")
    finally:
        conn.close()


def get_transactions():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
        SELECT id, date, type, category, amount, description
        FROM transactions
        ORDER BY date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except pymysql.Error as e:
        raise Exception(f"Database Error: {e}")
    finally:
        conn.close()



def get_all_transactions():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
        SELECT date, type, category, amount
        FROM transactions
        """
        cursor.execute(query)
        return cursor.fetchall()
    except pymysql.Error as e:
        raise Exception(f"Database Error: {e}")
    finally:
        conn.close()

def delete_transaction(trans_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM transactions WHERE id = %s"
        cursor.execute(query, (trans_id,))
        conn.commit()
    except pymysql.Error as e:
        raise Exception(f"Database Error: {e}")
    finally:
        conn.close()
