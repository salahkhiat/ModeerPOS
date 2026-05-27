import sqlite3 as db
from typing import List, Dict , Any
import os 
import shutil
from contextlib import contextmanager


from .shared_functions import SharedFunctions

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class DatabaseManager(SharedFunctions):
    def get_database_ref(self) -> str:
        """
        Return a full database reference. 
        
        :return: A database path.
        :rtype: str

        :example:
            >>> obj.get_database_ref()
            "./database_path/database.db"
        """
        settings = self.get_settings()
        return os.path.join(settings["database_path"], settings["database_name"])
    
    # Auto backup | database
    def db_auto_backup(self):
        """ make a database backup"""
        working_dir= self.get_settings()["database_path"]
        database = self.get_database_ref()
        backup_dir = os.path.join(working_dir, "database_backup")
        current_month_backup_dir = os.path.join(backup_dir, f"{self.current_date()[:7]}")
        
        current_date = f"{self.current_date()[:10]}.db"

        backup_file = os.path.join(current_month_backup_dir, current_date)
        
        # if database it not found, prepare it.
        if not os.path.isfile(database):
            logger.debug("preparing database ... ")
            self.prepare_database()
        
        # if a database is already exists.
        else:
            # If database_backup folder is not found, create it.
            if not os.path.isdir(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
                logger.debug(f"{backup_dir} directory has created.")

                # Create a current month backup directory.
                os.makedirs(current_month_backup_dir, exist_ok=True)

                # Make a first backup.
                shutil.copy2(database, backup_file)
                logger.debug(f"{backup_file} has created. ")

            # database_backup directory is already exists.  
            else:
                
                # If a current month backup directory is not found.
                if not os.path.isdir(current_month_backup_dir):

                    # Create it.
                    os.makedirs(current_month_backup_dir, exist_ok=True)

                    # Make a backup.
                    shutil.copy2(database, backup_file)
                    logger.debug(f"{backup_file} has created.")

                else:

                    # if there is no backup yet.
                    if not os.path.isfile(backup_file):

                        # Do it.
                        shutil.copy2(database, backup_file)
                        logger.debug(f"{backup_file} has created.")

                    else:
                 
                        # If the database has updated do .
                        # If last time file was modified do this part.
                        if os.path.getmtime(database) > os.path.getmtime(backup_file):
                            shutil.copy2(database, backup_file)
                            logger.debug(f"{backup_file} has updated.")
                            
                        else:
                            logger.debug(f"{backup_file} no need to update.")

    
    @contextmanager
    def db_connection(self):
        con = db.connect(self.get_database_ref())
        try:
            yield con 
        except db.Error as e:
            logger.exception(f"Database error:{e}")
            raise
        finally:
            con.close()

    
    def store(
            self, 
            table_name:str, 
            columns: list[str],
            data: tuple, 
            last_row_id:bool=False 
    )-> Any:
        """
        Insert data into a database table, return last_row_id if True.

        :param table_name: The name of the database table.
        :type table_name: str
        :param columns: A list of columns names.
        :type columns: list[str]
        :param data: A tuple of values.
        :type data: tuple
        :return: True or False If data inserted successfully or not, last_row_id if It was added as an Arg.
        :rtype: Any

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            # Prepare the SQL query
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

            cursor.execute(query,data)
            connection.commit()
            if last_row_id:
                return cursor.lastrowid
            else:
                return True
            
    def delete_item_from_db(self, table_name, where_clause, where_args):
        """
        Delete a row from a database table.

        Args:
            table_name (str):
                The table name to delete from.

            where_clause (str):
                The column name used in the WHERE condition.
                Example: "id"

            where_args (Any):
                The value for the WHERE condition.
                Example: 5

        Returns:
            bool:
                True if a row was deleted successfully,
                otherwise False.

        Example:
            self.delete_item_from_db(
                table_name="transactions",
                where_clause="id",
                where_args=5
            )
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"DELETE FROM {table_name} WHERE {where_clause} = ?"

            cursor.execute(query,(where_args,))
            connection.commit()

            if cursor.rowcount > 0: 
                return True 
            else: 
                return False

    def update_info(
        self, 
        table_name: str, 
        columns: list[str], 
        data: tuple, 
        where_clause: str, 
        where_args: tuple = ()
    ) -> bool:
        """
        Update data in a database table.

        :param table_name: The name of the database table.
        :type table_name: str
        :param columns: A list of column names to update.
        :type columns: list[str]
        :param data: A tuple of new values corresponding to the columns.
        :type data: tuple
        :param where_clause: SQL WHERE clause (e.g., "id = ?").
        :type where_clause: str
        :param where_args: Tuple of values for the WHERE clause placeholders.
        :type where_args: tuple
        :return: True if the update was successful, False otherwise.
        :rtype: bool

        Examples:
            >>># Update the 'name' and 'age' of the user where id=5
            >>>update('users', ['name', 'age'], ('Alice', 30), 'id = ?', (5,))
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            # Prepare the SQL query
            set_clause = ', '.join([f"{col} = ?" for col in columns])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

            # Combine data for SET and WHERE
            full_data = data + where_args

            cursor.execute(query, full_data)
            connection.commit()

            return cursor.rowcount > 0  # True if any row was updated

    
    def is_in_table(self, table:str,column:str , target:str) -> bool:
        """
        Check from an item by condition if exists.
        
        Args:
            table (str): the table name.
            target (str): the item name you're looking for.
            column (str): the table column.
        Returns:
            bool : True if the item exists, and False otherwise.
        
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"SELECT 1 FROM {table} WHERE {column} = ? LIMIT 1"
            cursor.execute(query,(target,))
            result = cursor.fetchone()

            if result is not None:
                return True
            else:
                return False 

    def add_column(self, table, column, default_value):
        """
        Add a new column with a default value to an existing table.
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]

            if column not in columns:
                    cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} TEXT DEFAULT '{default_value}'"
            )
            cursor.execute(
                f"UPDATE {table} SET {column} = '{default_value}' WHERE {column} IS NULL"
            )
            connection.commit()
            

    def search_by(self, table: str, column: str, keyword: str, target: str) -> Any:
        """
        Search for a single value in the database table based on a condition.
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"SELECT {target} FROM {table} WHERE {column} = ? LIMIT 1" 
            cursor.execute(query, (keyword,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return None
    
    def get_item_info(self, table: str, columns: tuple, keyword: str, target) -> dict | None:
        """
        Fetch a single row from a database table where a specific column matches a target value.

        Args:
            table (str): Name of the table (e.g. "products")
            columns (tuple): Columns to retrieve (e.g. ("barcode", "sale_price", "quantity"))
            keyword (str): The column used in the WHERE condition (e.g. "barcode" or "id")
            target: The value to match in the keyword column (e.g. 3434)

        Returns:
            dict | None: A dictionary representing one row, or None if not found.

            Examples:
                >>> table = "products"
                >>> columns = ("barcode", "sale_price", "quantity", "name")
                >>> keyword = "barcode"
                >>> target = 3434
                >>> item = obj.get_item_info(table, columns, keyword, target)
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            # dynamically construct query
            cols_str = ", ".join(columns)
            query = f"SELECT {cols_str} FROM {table} WHERE {keyword} = ? LIMIT 1"

            cursor.execute(query, (target,))
            row = cursor.fetchone()

            if row:
                # return a dictionary {column_name: value}
                return {col: val for col, val in zip(columns, row)}
            else:
                return None

    def search_by_similar(
            self, table: str, 
            column: str, 
            keyword: str, 
            target: List[str], 
            hide_deleted=True,
            hide_0_quantity_item = False
    ) -> List[Dict[str, Any]]:
        """
        Search for rows in a table where a column starts with a given keyword.
        Returns a list of dictionaries with the specified target columns.

        :param table: Name of the table to search
        :param column: Column to perform the LIKE search on
        :param keyword: The prefix keyword to search for
        :param target: List of columns to retrieve in the result
        :param hide_deleted: True to hide deleted targets
        :return: List of dictionaries with the requested columns
        """

        with self.db_connection() as connection: 
            cursor = connection.cursor()

            # Build the SELECT part dynamically from target list
            target_columns = ', '.join(target)
            # Query with parameterized LIKE for prefix search
            query = f"SELECT {target_columns} FROM {table} WHERE {column}  LIKE ? "
            
            if hide_0_quantity_item is True and table == "products":
                query += "AND quantity > 0"

            if hide_deleted is True:
                query += f" AND is_deleted = 0"
            
            if table == "customers":
                query += f" AND id != 1"
       
            cursor.execute(query, (f"%{keyword}%",))
            rows = cursor.fetchall()

            # Convert result rows to list of dicts
            results = []
            for row in rows:
                row_dict = dict(zip(target, row))
                results.append(row_dict)
            return results

    def is_db_table_empty(self, table: str) -> bool:
        """
        Check if a database table is empty.

        :param table: Name of the database table to check.
        :type table: str
        :return: True if the table is empty, False otherwise.
        :rtype: bool
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            query = f"SELECT 1 FROM {table} LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                return False  # Table has at least one row
            else:
                return True   # Table is empty

    def create_default_column(self, table:str, column:str, name:str = "-") -> bool:
        """
        Creating a default column if not exists.

        Args:
            table (str): The table name.
            column (str): The column name.
            name (str):the default user name.
        Returns:
            bool: True if the name was created successfully, False otherwise.
        """
        is_exists = self.is_in_table(table,column,name)
        if is_exists is False:
            return self.store(table,[column],(name))
        else:
            return False
            
    def get_table_as_list(
            self, 
            table: str, 
            columns: List[str],
            is_deleted=False
    ) -> List:
        """
        Returning table data as list.

        :param table: a table name.
        :type table: str
        :param columns: A list of columns names.
        :type columns: List[str]
        :return: A list rows.
        :rtype: List

        :examples:
            >>> table = "students"
            >>> columns = ["name","class","degree"]
            >>> obj.get_table_as_list(table,columns)
            ["Muhammed", "Nooh", "Adam" ]
        """

        with self.db_connection() as connection: 
            cursor = connection.cursor()
            table_columns = ", ".join(columns)
            query = f"SELECT {table_columns} FROM {table}"
            if is_deleted is True:
                query += " WHERE is_deleted=0"
            data = cursor.execute(query).fetchall()
            new_data = [item[0] for item in data]
            
            return new_data

    
    def get_table_as_dict(self, table:str, column:str) -> Dict:
        """
        Returning table data as dictionary {"id":"column"}.
        
        Args:
            table (str): The table name.
            column (str): The table column.
        Returns:
            dict: Data as dictionary.
        Examples:
            >>> table = "student"
            >>> column = "name"
            >>> obj.get_table_as_dict(table,column)
            {1:"Muhammed", 2:"Ahmed"}
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            
            query = f"SELECT id, {column} FROM {table}"
        

            data = cursor.execute(query).fetchall()

            new_data = {item[0]:item[1] for item in data}
            return new_data

    def get_table_cols_list(
            self, 
            table:str, 
            columns:List[str], 
            where_clause:str=None, 
            parms: tuple=(),
            union=False
        ) -> List:
        
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = None 
            if table == "suppliers_transactions":
                return self.get_suppliers_transactions_list()
            
            elif table == "customers_transactions":
                return self.get_customers_transactions_list()
            
            elif table == "employees_transactions":
                return self.get_employees_withdrawals_list()
            
            elif table == "expenses":
                return self.get_expenses_list()
            
            elif table == "purchases_history":
                return self.get_purchases_history_list()
            
            elif table == "sales_history":
                return self.get_sales_history_list()
            
            elif table == "purchases_invoices":
                return self.get_purchases_invoices_list()
            
            elif table == "sales_invoices":
                return self.get_sales_invoices_list()
            
            elif table == "services":
                return self.get_services_list()
            
            elif table == "services_categories":
                return self.get_services_categories_list()
            
            elif table == "expenses_categories":
                return self.get_expenses_categories_list()
            
            else:
                created = self.current_date()[:10]
                
                query = f"SELECT {','.join(columns)} FROM {table}" 

                ordering = f" WHERE st.created LIKE '{created}%' ORDER BY created DESC; "
                if  where_clause:
                    query += f" WHERE {where_clause}"
                    
                    if table == "customers":
                        query += f" AND id != 1"
                if union:
                    query += f" AS combined"
              
                
            
                return cursor.execute(query, parms).fetchall()

    def get_customers_transactions_list(self, keyword=None, limit=15, offset=0) -> List:
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            query = f"""
                SELECT * FROM
                ( 
                    SELECT
                        p.id AS id,
                        c.name AS name,
                        p.note AS description,
                        'payment' AS process,
                        p.amount AS amount, 
                        p.created AS created
                    FROM 
                        customers_payments p 
                    JOIN
                        customers c 
                    ON 
                        p.customer_id = c.id 
                    WHERE 
                        c.id != 1
                    AND 
                        c.is_deleted = 0
                    
                        
                    UNION ALL 

                    SELECT
                        s.id AS id,
                        c.name AS name,
                        s.description AS description,
                        'service' AS process,
                        s.paid_price AS amount,
                        s.created AS created
                    FROM 
                        customers c
                    JOIN 
                        services s 
                    ON 
                        c.id = s.customer_id
                    WHERE
                        c.id != 1
                    AND 
                        c.is_deleted = 0
                    
                    UNION ALL
                    SELECT
                        si.id AS id,
                        c.name AS name,
                        si.invoice_number AS description,
                        'sale' AS process,
                        si.deposit AS amount,
                        si.created_at AS created
                    FROM
                        customers c
                    JOIN
                        sale_invoices si
                    ON
                        c.id = si.customer_id
                    WHERE 
                        c.id != 1
                    AND 
                        c.is_deleted = 0
                        
                ) AS compined 
                WHERE 
                    amount > 0 
               
            """ 
            conditions = []
            params = []

            if keyword:
                conditions.append(" name LIKE ? ")
                params.append(f"%{keyword}%")
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            query += " ORDER BY created DESC LIMIT ? OFFSET ?"
            
            params.extend([limit, offset])
            result = cursor.execute(query, params).fetchall()

            return result



    def get_pieces_transactions_list(self, keyword=None, status=None, limit=10, offset=0) -> List:
        with self.db_connection() as connection: 
            cursor = connection.cursor()
        
            created = self.current_date()
            query = f"""
        
                    SELECT
                        p.id AS id,
                        s.name AS supplier,
                        p.piece AS name,
                        p.price AS price,
                        p.status AS status,
                        p.created AS created
                    
                    FROM 
                        suppliers s 
                    JOIN
                        pieces_transactions p 
                    ON 
                        p.supplier_id = s.id 
              
            """ 
            conditions = []
            params = []

            if status:
                conditions.append("p.status = ?")
                params.append(status)
                
            if keyword:
                conditions.append("s.name LIKE ?")
                params.append(f"%{keyword}%")
                

            # ✅ Add WHERE only once
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY p.created DESC LIMIT ? OFFSET ?"
            
            params.extend([limit, offset])
            

            result = cursor.execute(query, params).fetchall()
            
            return result
        
    def get_suppliers_transactions_list(self, keyword=None, limit=10, offset=0) -> List:
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            query = f"""
                SELECT 
                    st.id AS id,
                    s.name AS name, 
                    st.note AS note, 
                    st.type AS _type,
                    st.amount AS amount, 
                    st.created AS created
                FROM
                    suppliers_transactions st
                JOIN 
                    suppliers s 
                ON s.id = st.supplier_id
            """ 
            conditions = []
            params = []
            

            if keyword:
                conditions.append(" name LIKE ? ")
                params.append(f"%{keyword}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            
            params.extend([limit, offset])
            result = cursor.execute(query, params).fetchall()
            return result

    def get_employees_withdrawals_list(self, keyword=None, limit=10, offset=0) -> List:
        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            query = f"""
                SELECT 
                    withd.id AS id,
                    emp.name AS name,
                    withd.note AS note,
                    withd.amount AS amount,
                    withd.created AS created
                FROM
                    employees emp
                JOIN
                    employees_withdrawals withd
                ON 
                    emp.id = withd.employee_id
            """ 
            
            conditions = []
            params = []

            if keyword:
                conditions.append(" name LIKE ? ")
                params.append(f"%{keyword}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            
            params.extend([limit, offset])
            result = cursor.execute(query, params).fetchall()
            return result

    def get_expenses_list(self, keyword=None, limit=10, offset=0) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
         
            query = f"""
                SELECT 
                    exp.id AS id,
                    exp.note AS note,
                    c.name AS category,
                    exp.amount AS amount,
                    exp.created AS created

                FROM
                    expenses_categories c

                JOIN
                    expenses exp
                ON 
                    c.id = exp.category_id
            """ 
            conditions = []
            params = []

            if keyword:
                conditions.append(" note LIKE ? ")
                params.append(f"%{keyword}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            
            params.extend([limit, offset])
            result = cursor.execute(query, params).fetchall()
            return result

    def get_purchases_history_list(self, keyword=None) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            created = self.current_date()[:7]
            query = f"""
                SELECT 
                    p.product_name AS name,
                    p.barcode AS barcode,
                    p.purchase_price AS price,
                    p.quantity AS quantity,
                    p.total AS total,
                    inv.invoice_number AS invoice,
                    inv.created_at AS created
                FROM
                    purchase_invoices inv

                JOIN
                    purchases_history p
                ON 
                    inv.id = p.invoice_id
            """ 
            result = None
            ordering = f" ORDER BY inv.created_at DESC; "
            if keyword:
                query += " WHERE name LIKE ? " + ordering
                result = cursor.execute(query,(f"%{keyword}%",)).fetchall()
                
            else:
                query += ordering
                result = cursor.execute(query).fetchall() 
            return result

    def get_sales_history_list(self, keyword=None) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            query = f"""
                SELECT 
                    s.product_name AS name,
                    s.barcode AS barcode,
                    s.sale_price AS price,
                    s.quantity AS quantity,
                    s.total AS total,
                    inv.invoice_number AS invoice,
                    inv.created_at AS created
                FROM
                    sale_invoices inv

                JOIN
                    sales_history s
                ON 
                    inv.id = s.invoice_id
            """ 
            result = None
            ordering = f" ORDER BY inv.created_at DESC; "
            if keyword:
                query += " AND name LIKE ? " + ordering
                result = cursor.execute(query,(f"%{keyword}%",)).fetchall()
            else:
                query += ordering
                result = cursor.execute(query).fetchall()
                
            return result

    def get_purchases_invoices_list(self, keyword=None) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            query = f"""
                SELECT 
                    name,
                    invoice_number,
                    total,
                    deposit,
                    created_at
                FROM
                    purchase_invoices inv

                JOIN
                    suppliers s
                ON 
                    s.id = inv.supplier_id
            """ 
            result = None
            ordering = f" ORDER BY inv.created_at DESC; "
            if keyword:
                query += " AND name LIKE ? " + ordering
                result = cursor.execute(query,(f"%{keyword}%",)).fetchall()
            else:
                query += ordering
                result = cursor.execute(query).fetchall()
                
            return result

    def get_sales_invoices_list(self, keyword=None) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            query = f"""
                SELECT 
                    name,
                    invoice_number,
                    total,
                    deposit,
                    created_at
                FROM
                    sale_invoices inv

                JOIN
                    customers c
                ON 
                    c.id = inv.customer_id
            """ 
            result = None
            ordering = f" ORDER BY inv.created_at DESC; "
            if keyword:
                query += " AND name LIKE ? " + ordering
                result = cursor.execute(query,(f"%{keyword}%",)).fetchall()
            else:
                query += ordering
                result = cursor.execute(query).fetchall()
                
            return result
                
    def get_services_list(self, keyword=None, limit=10, offset=0) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            query = f"""
                SELECT 
                    ser.id AS service_id,
                    ser.description AS description,
                    cus.name AS customer,
                    cate.name AS category,
                    ser.default_price AS price,
                    ser.paid_price AS paid,
                    ser.created AS created
                FROM
                    customers cus

                JOIN
                    services ser
                ON 
                    cus.id = ser.customer_id
                JOIN
                    services_categories cate
                ON 
                    ser.category_id = cate.id 
            """ 

            conditions = []
            params = []

      

            if keyword:
                conditions.append("cus.name LIKE ?")
                params.append(f"%{keyword}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY ser.created DESC LIMIT ? OFFSET ?"

            params.extend([limit, offset])
            result = cursor.execute(query, params).fetchall()

                
            return result
    def get_products_list(self, keyword=None, limit=10, offset=0) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            query = f"""
                SELECT
                    barcode,
                    name,
                    quantity,
                    purchase_price,
                    sale_price,
                    is_deleted
                FROM 
                    products

            """ 

            conditions = []
            params = []
            conditions.append("is_deleted = 0")

            if keyword:
                conditions.append("(name LIKE ? OR barcode LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            
            params.extend([limit, offset])
            result = cursor.execute(query, params).fetchall()

            return result

    def get_services_categories_list(self, keyword=None) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            created = self.current_date()[:7]
            query = f"""
               SELECT
                    c.id,
                    c.name AS category_name,
                    COUNT(s.category_id) AS services_count,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN s.customer_id = 1 THEN s.default_price
                                ELSE s.paid_price
                            END
                        ), 0
                    ) AS total_money
                FROM
                    services_categories c
                LEFT JOIN
                    services s
                ON
                    s.category_id = c.id
                WHERE 
                    s.created LIKE '{created}%'
                AND 
                    c.is_deleted = 0
            """ 
            result = None
            ordering = f"GROUP BY c.id, c.name ORDER BY category_name; "
            if keyword:
                query += " AND c.name LIKE ? " + ordering
                result = cursor.execute(query,(f"%{keyword}%",)).fetchall()
            else:
                query += ordering
                result = cursor.execute(query).fetchall()
                
            return result
                
    def get_expenses_categories_list(self, keyword=None) -> List:

        with self.db_connection() as connection: 
            cursor = connection.cursor()
 
            created = self.current_date()[:7]
            query = f"""
               SELECT
                    c.id,
                    c.name AS category_name,
                    COUNT(exp.category_id) AS expenses_count,
                    COALESCE(
                        SUM(amount), 0) AS total_money
                FROM
                    expenses_categories c
                LEFT JOIN
                    expenses exp
                ON
                    exp.category_id = c.id
                WHERE 
                    exp.created LIKE '{created}%'
                AND 
                    c.is_deleted = 0
            """ 
            result = None
            ordering = f"GROUP BY c.id, c.name ORDER BY category_name; "
            if keyword:
                query += " AND c.name LIKE ? " + ordering
                result = cursor.execute(query,(f"%{keyword}%",)).fetchall()
            else:
                query += ordering
                result = cursor.execute(query).fetchall()
                
            return result

    def tel_exists(self,table: str, tel: str, user_id=None ) -> bool:
        """
        Return True if a tel  exists in the provided table, False otherwise.
        :example:
            >>> obj.tel_exists("contacts", "1234567890")
            True
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"SELECT 1 FROM {table} WHERE tel = ?"
            
            args = [tel, ]
            if user_id is not None:
                query += f" AND id != ?"
                args.append(user_id)
            
            query += " LIMIT 1"

            cursor.execute(query, args)
            

            return cursor.fetchone() is not None

    def is_belonged_to_other(self, current_id:str, current_barcode:str):
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"SELECT 1 FROM products WHERE id != ? AND barcode = ? LIMIT 1"
            cursor.execute(query,(str(current_id), str(current_barcode)))
            result = cursor.fetchone()
            return result is not None

    def get_sales_cash(self,s_date:str="today") -> float:
        """
        Calculate total sales income based on conditional rules.

        Rules:
        - If customer_id == 1:
            - If deposit == 0 → use total
            - If deposit > 0 → use deposit
        - If customer_id != 1:
            - Always use deposit

        :return: Calculated sales income.
        :rtype: float
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT SUM(
                    CASE
                        -- WHEN customer_id = 1 AND deposit = 0 THEN total
                        -- WHEN customer_id = 1 AND deposit > 0 THEN deposit
                        WHEN customer_id = 1 THEN total
                        ELSE deposit
                    END
                )
                FROM 
                    sale_invoices
                WHERE 
                    created_at LIKE ?

            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0

    def get_services_cash(self, s_date:str="today") -> float:
        """
        Calculate total services cash based on conditional rules.

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT SUM(
                    CASE
                        WHEN customer_id = 1  THEN default_price
                        ELSE paid_price
                    END
                )
                FROM services
                WHERE created LIKE ? 
            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0

    def get_sales_capital(self,s_date:str="today") -> float:
        """
        Calculate total sales capital (sum of invoice capitals) for the current month.
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT SUM(sh.purchase_price * sh.quantity)
                FROM sales_history sh
                JOIN sale_invoices si ON si.id = sh.invoice_id
                WHERE si.created_at LIKE ?
            """
            cursor.execute(query, (f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0

    def get_expenses(self,s_date:str="today") -> float:
        """
        Calculate total expenses  based on conditional rules.

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT SUM(amount)
                FROM expenses
                WHERE created LIKE ? 
            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0

    def get_suppliers_deposits(self,s_date:str="today") -> float:
        """
        Calculate deposits to suppliers  based on conditional rules.

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT SUM(
                    CASE
                          WHEN type = 'deposit' THEN amount
                    END
                )
                FROM suppliers_transactions
                WHERE created LIKE ? 
            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0
                
    def get_suppliers_debts(self,s_date:str="today") -> float:
        """
        Calculate deposits to suppliers  based on conditional rules.

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT SUM(
                    CASE
                          WHEN type = 'debt' THEN amount
                    END
                )
                FROM suppliers_transactions
                WHERE created LIKE ? 
            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0

    def get_purchases_deposits(self,s_date:str="today") -> float:
        """
        Calculate deposits to suppliers  based on purchase_invoices and conditional rules.

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT SUM(deposit)
                FROM purchase_invoices
                WHERE created_at LIKE ? 
            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0

    def get_customers_cash(self,s_date:str="today") -> float:
        """
        Calculate total customer_payments  based on conditional rules.

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06
            query = """
                SELECT 
                    SUM(amount)
                FROM 
                    customers_payments
                WHERE 
                    created LIKE ?
            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0

    def get_employees_withdrawals(self,s_date:str="today") -> float:
        """
        Calculate total employees_withdrawals  based on conditional rules.

        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            created = self.current_date()[:10] # 1447-06-01
            if s_date == "month":
                created = self.current_date()[:7] # 1447-06

            query = """
                SELECT 
                    SUM(amount)
                FROM 
                    employees_withdrawals
                WHERE 
                    created LIKE ?
            """
            cursor.execute(query,(f"{created}%",))
            result = cursor.fetchone()

            return result[0] if result and result[0] is not None else 0.0
    
    def get_supplier_transactions_sum(self, tran_type: str, user_id: int) -> float:
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = """
                SELECT SUM(amount)
                FROM suppliers_transactions
                WHERE type = ?
                AND supplier_id = ? 
            """
            cursor.execute(query,(tran_type, user_id))
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.0

    def get_supplier_purchase_sum(self, col_name: str, user_id: int) -> float:
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"""
                SELECT SUM({col_name})
                FROM purchase_invoices
                WHERE supplier_id = ? 
            """
            cursor.execute(query,(user_id,))
            result = cursor.fetchone()
            
            return result[0] if result and result[0] is not None else 0.0

    def get_customer_payment_sum(self, customer_id: int) -> float:
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"""
                SELECT SUM(amount)
                FROM customers_payments
                WHERE customer_id = ? 
            """
            cursor.execute(query,(customer_id,))
            result = cursor.fetchone()
            
            return result[0] if result and result[0] is not None else 0.0
        
    def get_customer_deposit_sum(self, customer_id: int) -> float:
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"""
                SELECT SUM(deposit)
                FROM sale_invoices
                WHERE customer_id = ? 
            """
            cursor.execute(query,(customer_id,))
            result = cursor.fetchone()
            
            return result[0] if result and result[0] is not None else 0.0

    def get_customer_service_sum(self, customer_id: int) -> float:
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"""
                SELECT SUM(paid_price)
                FROM services
                WHERE customer_id = ? 
            """
            cursor.execute(query,(customer_id,))
            result = cursor.fetchone()
            
            return result[0] if result and result[0] is not None else 0.0

    def get_col_sum(self, table:str, col:str, where_item:str, target:int) -> float:
        """ 
        Sum the col according to the where_item and target.
        
        Args:
            table (str): The table name.
            col (str): The table column.
            where_item (str): what need to be compared with it (e.g. customer_id column).
            target (int): what should be compared with where_item (e.g. customer_id=89) or any ID.
        Returns:
            float: The sum of the entire selected column.
        """
        with self.db_connection() as connection: 
            cursor = connection.cursor()
            query = f"""
                SELECT SUM({col})
                FROM {table}
                WHERE {where_item} = ? 
            """
            cursor.execute(query,(target,))
            result = cursor.fetchone()
            
            return result[0] if result and result[0] is not None else 0.0
        
    def get_units_sold_count(self, customer_id: int, product_barcode: int) -> int:
        """ 
        Returns total units sold of a specific customer and product during the current month
        """

        with self.db_connection() as connection:
            cursor = connection.cursor()
            created = self.current_date()[:7]
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
                        sh.barcode = ? 
                    AND
                        inv.created_at LIKE ?

            """
            args = (customer_id, product_barcode, f"{created}%")
            
            return cursor.execute(query, args).fetchone()[0]
        
    def prepare_database(self) :
        """
        Create a database and its tables if they not exists.
        """
        
        with self.db_connection() as connection: 
            cursor = connection.cursor()

            # List of SQL commands to create each table
            create_tables_sql = [
                # Suppliers
                """
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    tel TEXT,
                    is_deleted BOOLEAN DEFAULT 0
                );
                """,

                # Customers
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    tel TEXT,
                    is_deleted BOOLEAN DEFAULT 0
                );
                """,

                # Employees
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    tel TEXT,
                    is_deleted BOOLEAN DEFAULT 0
                );
                """,

                # Suppliers Invoices
                """
                CREATE TABLE IF NOT EXISTS purchase_invoices (
                    id INTEGER PRIMARY KEY,
                    supplier_id INTEGER NOT NULL,
                    invoice_number TEXT,           -- Optional: unique invoice code
                    total TEXT,
                    deposit TEXT,
                    created_at TEXT ,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                );

                """,

                # Product
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    barcode TEXT,
                    name TEXT NOT NULL,
                    purchase_price REAL,
                    sale_price REAL,
                    quantity INTEGER,
                    invoice_id INTEGER,
                    is_deleted BOOLEAN DEFAULT 0,  -- Soft delete flag
                    FOREIGN KEY (invoice_id) REFERENCES purchase_invoices(id)
                );

                """,

                # purchases_history
                """
                CREATE TABLE IF NOT EXISTS purchases_history (
                    id INTEGER PRIMARY KEY,
                    invoice_id INTEGER NOT NULL,
                    product_id INTEGER,                 -- FK to products, nullable if you allow free-text items
                    product_name TEXT NOT NULL,        -- Snapshot of name
                    barcode TEXT,                      -- Optional snapshot of barcode
                    quantity INTEGER NOT NULL,
                    purchase_price REAL NOT NULL,      -- Snapshot of price at purchase time
                    sale_price REAL,                   -- Optional: expected sale price
                    total REAL GENERATED ALWAYS AS (quantity * purchase_price) STORED,  -- Auto-calculated
                    FOREIGN KEY (invoice_id) REFERENCES purchase_invoices(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );

                """,

                # Customers Invoices
                """
                CREATE TABLE IF NOT EXISTS sale_invoices (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    invoice_number TEXT,           -- Optional: unique invoice code
                    total TEXT,
                    deposit TEXT,
                    created_at TEXT ,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                );
                """,

                # Sales History
                """
                CREATE TABLE IF NOT EXISTS sales_history (
                    id INTEGER PRIMARY KEY,
                    invoice_id INTEGER NOT NULL,
                    product_id INTEGER,                 -- FK to products, nullable if you allow free-text items
                    product_name TEXT NOT NULL,        -- Snapshot of name
                    barcode TEXT,                      -- Optional snapshot of barcode
                    quantity INTEGER NOT NULL,
                    purchase_price REAL NOT NULL,      -- Snapshot of price at sale time
                    sale_price REAL,                   -- Optional: expected sale price
                    total REAL GENERATED ALWAYS AS (quantity * sale_price) STORED,  -- Auto-calculated
                    FOREIGN KEY (invoice_id) REFERENCES sale_invoices(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
                """,

                # Suppliers Transactions
                """
                CREATE TABLE IF NOT EXISTS suppliers_transactions (
                    id INTEGER PRIMARY KEY,
                    supplier_id INTEGER,
                    invoice_id INTEGER,             -- ✅ NEW: optional link to a purchase invoice
                    note TEXT,
                    amount REAL,
                    type TEXT,                      -- e.g., 'debt', 'deposit'
                    created TEXT,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
                    FOREIGN KEY (invoice_id) REFERENCES purchase_invoices(id)  -- ✅ new FK
                );

                """,

                # Employees Withdrawals
                """
                CREATE TABLE IF NOT EXISTS employees_withdrawals (
                    id INTEGER PRIMARY KEY,
                    employee_id INTEGER,
                    note TEXT,
                    amount REAL,
                    created TEXT,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );
                """,

                # Pieces transactions
                """
                CREATE TABLE IF NOT EXISTS pieces_transactions (
                    id INTEGER PRIMARY KEY,
                    supplier_id INTEGER,
                    piece TEXT,
                    price REAL,
                    status TEXT,
                    created TEXT,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                );
                """,

                # Expenses Categories
                """
                CREATE TABLE IF NOT EXISTS expenses_categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_deleted BOOLEAN DEFAULT 0
                );
                """,

                # Expenses
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    note TEXT,
                    amount REAL,
                    category_id INTEGER,
                    created TEXT,
                    FOREIGN KEY (category_id) REFERENCES expenses_categories(id)
                );
                """,

                # Services Categories
                """
                CREATE TABLE IF NOT EXISTS services_categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_deleted BOOLEAN DEFAULT 0  -- Soft delete flag
                );
                """,

                # Services
                """
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    category_id INTEGER,
                    description TEXT,
                    default_price REAL,
                    paid_price REAL,
                    created TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (category_id) REFERENCES services_categories(id)
                );
                """,

                # Customers Payments
                """
                CREATE TABLE IF NOT EXISTS customers_payments (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    amount REAL,
                    note TEXT,
                    created TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                );
                """,

                # Mobiles
                """
                CREATE TABLE IF NOT EXISTS mobiles (
                    id INTEGER PRIMARY KEY,
                    model TEXT,
                    color TEXT,
                    price REAL,
                    serial TEXT,
                    note TEXT,
                    seller_name TEXT,
                    seller_tel TEXT,
                    seller_identify_id TEXT,
                    document_type INTEGER,
                    created TEXT,
                    FOREIGN KEY (document_type) REFERENCES documents_types(id)
                );
                """,

                # Documents Types
                """
                CREATE TABLE IF NOT EXISTS documents_types (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
                """,

                # Requested Products
                """
                CREATE TABLE IF NOT EXISTS requested_products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created TEXT
                );
                """
            ]

            # Execute each create table statement
            for sql in create_tables_sql:
                cursor.execute(sql)

            # Commit changes and close connection
            connection.commit()
       
        # Default settings
        self.create_default_column("customers", "name")
        self.create_default_column("expenses_categories", "name")

        # Add an X column to an existing table
        self.add_column("customers", "user_type", "normal")
        self.add_column("services", "piece_price", 0)
        
        logger.info("Database tables created successfully.")
    