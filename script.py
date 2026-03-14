import sqlite3 
import logging
from contextlib import contextmanager 

logging.basicConfig(
    filename='file.log',
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
)

@contextmanager
def db_connection():
    con = sqlite3.connect("data.db")
    try:
        yield con 
    except sqlite3.Error as e:
        logging.exception(f"Database error:{e}")
        raise
    finally:
        con.close()
        
        
    

def connection():
    with db_connection() as con:
        cursor = con.cursor()
        query = f"""
                SELECT 
                    COALESCE(sum(sh.quantity), 0) AS total_sold
                FROM
                    sales_history sh
                JOIN
                    sale_invoices inv
                ON  
                    sh.invoice_id = inv.id
                WHERE
                    inv.customer_id = ?
                AND
                    sh.product_id = ? 
                AND
                    inv.created_at LIKE ?

        """
        fltr = (2, 3, "1447-09%")
        
        return cursor.execute(query,fltr).fetchone()[0]
    
a = 15
b = (-a)
print(b)



