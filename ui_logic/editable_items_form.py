from .base_form import Form

from typing import List
from PyQt6.QtWidgets import  QTableWidget, QLineEdit, QPushButton, QWidget

from .account_form import AccountForm
from uis.account import Ui_Form as AccountFormUi

from .item_form import ItemForm
from uis.item import Ui_Form as ItemFormUi

from .category_form import CategoryForm 
from uis.category import Ui_Form as CategoryFormUi

from PyQt6.QtCore import QTimer

from .error_form import ErrorForm
from uis.error_msg import Ui_Dialog as ErrorFormUi

from .confirmation_msg_form import ConfirmationMsgForm
from uis.confirmation_msg import Ui_Dialog as ConfirmationMsgFormUi

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class EditableItemsForm(Form):
    
    def __init__(self,base_form):
        super().__init__(base_form)
        # set icons
        self.set_icon("edit_btn","edit.svg")
        self.set_icon("delete_btn","delete.svg")

        # default settings
        self.qt_table: QTableWidget = self.ui.table 
        self.db_table: str = None
        self.columns: List = None 
        self.item_id: int = None 
        self.update_variable_on_row_select(self.qt_table, "item_id", 0)
        self.ACCOUNT_TYPES = ["suppliers", "customers", "employees"]
        self.font_size = 16

        # is_deleted column exists.
        self.IS_DELETED_COL_ON =[
            "products", 
            "services_categories", 
            "expenses_categories"
        ] + self.ACCOUNT_TYPES 

        # delete and/or edit buttons are allowed
        self.DEL_EDIT_BTNS_ALLOWED = [
            "services_categories",
            "expenses_categories"
        ] + self.IS_DELETED_COL_ON  
        
        self.ONLY_DEL_BTN_ALLOWED = ["requested_products", "mobiles"]

        # obj.column for database searchs purposes : SELECT column FROM ...
        self.column: str = "name" 
        
        # Search box
        search_box: QLineEdit = self.ui.search_box
        search_box.textChanged.connect(self.search_box)

        # connect buttons
        self.ui.edit_btn.clicked.connect(self.show_edit_form)
        self.ui.delete_btn.clicked.connect(self.delete_item)

    def show_err_msg(self,msg:str):
        self.play_failure_sound()
        form = ErrorForm(ErrorFormUi)
        form.ui.err_msg.setText(msg.strip())
        QTimer.singleShot(2000,form.close)
        form.exec()
        
    def set_db_table_info(
        self,
        table_widget: QTableWidget, 
        db_table: str, 
        columns: List[str],
        font_size: int = 16,
        data = None
    ) -> None:
        
        # set default table data
        self.qt_table = table_widget
        self.db_table = db_table
        self.columns = columns
        self.variable = None 
        self.font_size = font_size

        # disable buttons
        self.disable_delete_edit_btns()
        
        self.refresh_table(data)


    def refresh_table(self, data=None):
        items = None
        if data == None:
            if self.db_table not in self.IS_DELETED_COL_ON:
                items = self.get_table_cols_list(self.db_table, self.columns) 
            else:
            
                items = self.get_table_cols_list(
                self.db_table, self.columns, 'is_deleted = ?', (0, )
                )

        else:
            items = data
        
        if  self.db_table in self.ACCOUNT_TYPES:
            # Make the columns of Qt meet the db_table.
            self.qt_table.setColumnCount(len(self.columns)+1) 
        else:
            self.qt_table.setColumnCount(len(self.columns)) 

        for item in items:
            item = list(item)
            if self.db_table == "suppliers":
                balance = self.get_user_balance("supplier", item[0])
                item.append(balance)
            
            elif self.db_table == "customers":
                balance = self.get_user_balance("customer", item[0])
                item.append(balance)
            
            elif self.db_table == "employees":
                balance = self.get_user_balance("employee", item[0])
                item.append(balance)
                
            # where the next row should go
            row = self.qt_table.rowCount() 
            
            # insert new row at the bottom of the table
            self.qt_table.insertRow(row) 

            for col_id, col_info in enumerate(item):
                    table_item = self.make_item(
                        col_info, font_size=self.font_size, read_only=True
                    )
                    self.qt_table.setItem(row, col_id, table_item)
    
    def disable_delete_edit_btns(self):
        if self.db_table in self.ONLY_DEL_BTN_ALLOWED:
            self.disable_edit_btn()

        elif self.db_table not in self.DEL_EDIT_BTNS_ALLOWED:
            self.disable_delete_btn()
            self.disable_edit_btn()

    def disable_edit_btn(self, cmd=False):
        edit_btn: QPushButton = self.ui.edit_btn
        edit_btn.setEnabled(cmd)
        if cmd is False:
            edit_btn.setStyleSheet("border: 1px;background: gray;")

    def disable_delete_btn(self, cmd=False):
        delete_btn: QPushButton = self.ui.delete_btn
        delete_btn.setEnabled(cmd)
        if cmd is False:
            delete_btn.setStyleSheet("border: 1px;background: gray;")

            
    def supplier_balance(self, supplier_id:int):
        transactions_deposits = self.get_supplier_transactions_sum("deposit", supplier_id)
        purchases_deposits = self.get_supplier_purchase_sum("deposit", supplier_id)
        deposits = transactions_deposits + purchases_deposits

        transactions_debts = self.get_supplier_transactions_sum("debt", supplier_id)
        purchases_total = self.get_supplier_purchase_sum("total", supplier_id)
        debts = transactions_debts + purchases_total
        
        return debts - deposits
    
    def customer_balance(self, customer_id:int):

        sales = self.get_col_sum(
            "sale_invoices",
            "total",
            "customer_id",
            customer_id
        )
        services = self.get_col_sum(
            "services",
            "default_price",
            "customer_id",
            customer_id
        )
        all_debts = sales + services

        payments = self.get_col_sum(
            "customers_payments",
            "amount",
            "customer_id",
            customer_id
        )

        deposits = self.get_col_sum(
            "sale_invoices",
            "deposit",
            "customer_id",
            customer_id
        )

        services_paids = self.get_col_sum(
            "services",
            "paid_price",
            "customer_id",
            customer_id
        )

        all_payments = payments + deposits + services_paids
        
        return all_debts - all_payments
    
    def employee_balance(self, employee_id:int):

        withdrawals = self.get_col_sum(
            "employees_withdrawals",
            "amount",
            "employee_id",
            employee_id
        )
        return withdrawals

    def get_user_balance(self, account_type: str, user_id: int) -> float:
        if account_type == "supplier":
            return self.supplier_balance(user_id)
        
        elif account_type == "customer":
            return self.customer_balance(user_id)
        
        elif account_type == "employee":
            return self.employee_balance(user_id)

        raise ValueError(f"Unsupported account type: {account_type}")
    
    def search_box(self, search_word: str) -> None:

        self.qt_table.setRowCount(0)
        search_word = str(search_word).strip()
        items = None 
        data = None 

        if self.db_table == "suppliers_transactions":
            data = self.get_suppliers_transactions_list(search_word)

        if self.db_table == "customers_transactions":
            data = self.get_customers_transactions_list(search_word)
            
        elif self.db_table == "employees_transactions":
            data = self.get_employees_withdrawals_list(search_word)
        elif self.db_table == "expenses":
            data = self.get_expenses_list(search_word)
        elif self.db_table == "purchases_history":
            data = self.get_purchases_history_list(search_word)
        elif self.db_table == "sales_history":
            data = self.get_sales_history_list(search_word)
        elif self.db_table == "purchases_invoices":
            data = self.get_purchases_invoices_list(search_word)
        elif self.db_table == "sales_invoices":
            data = self.get_sales_invoices_list(search_word)
        elif self.db_table == "services":
            data = self.get_services_list(search_word)
        elif self.db_table == "services_categories":
            data = self.get_services_categories_list(search_word)
        elif self.db_table == "expenses_categories":
            data = self.get_expenses_categories_list(search_word)
        

        else:
            items = self.search_by_similar(
                self.db_table, self.column, search_word, self.columns
            )
            data = [ tuple(item.values()) for item in items]

        self.set_db_table_info(self.qt_table, self.db_table, self.columns, 16, data)

    def show_edit_form(self):

        if self.item_id is None:
            self.select_item_warning()
            return 
        
        # When table is suppliers, customers, employees
        users_table = ["suppliers", "customers", "employees"]

        if self.db_table in users_table:
            user_info = self.get_item_info(
                self.db_table,
                ("name", "tel"),
                "id",
                self.item_id
            )
       
            form: QWidget = AccountForm(AccountFormUi, self.item_id, self.db_table)
            form.setWindowTitle(user_info["name"])
            form.ui.name.setText(user_info["name"])
            form.ui.tel.setText(user_info["tel"])

            account_placeholder = {
                "suppliers": "مورد",
                "customers": "زبون",
                "employees": "عامل"
            }
            form.ui.account_type.setItemText(0, account_placeholder[self.db_table])
            form.ui.account_type.setEnabled(False)
            form.exec()
    
        # When table is products
        if self.db_table == "products":
            product_information = self.get_item_info(
                self.db_table,
                (
                    "barcode", 
                    "name", 
                    "quantity", 
                    "sale_price", 
                    "purchase_price"
                ),
                "barcode",
                self.item_id
            )
            # product_info = product_information.values()
            barcode = product_information["barcode"]
            name = product_information["name"]
            quantity = product_information["quantity"]
            sale_price = product_information["sale_price"]
            purchase_price = product_information["purchase_price"]

            form = ItemForm(ItemFormUi,self.item_id)
            form.set_icon("add_btn","apply.svg")
            form.setWindowTitle(name)
            form.ui.title.setText(name)
            form.ui.ref.setText(barcode)
            form.ui.name.setText(name)
            form.ui.quantity.setText(str(quantity))
            form.ui.purchase_price.setText(f"{purchase_price:.0f}")
            form.ui.sale_price.setText(f"{sale_price:.0f}")
            form.item_updated.connect(self.refresh_table)
            form.exec()

        if self.db_table in ["services_categories", "expenses_categories"]:
            category_name = self.get_item_info(
                self.db_table, ("name",), "id", self.item_id
            )["name"]
            form = CategoryForm(CategoryFormUi, self.item_id)
            form.setWindowTitle(category_name)
            form.ui.title.setText(category_name)
            form.ui.name.setText(category_name)
            form.category_saved.connect(lambda _: self.refresh_table())
            form.exec()
            
        self.qt_table.setRowCount(0)
        self.refresh_table()
    
    def on_delete_confirmed(self, confirmed: bool):
        if not confirmed:
            return
        
        # 2 then delete
        form = None

        if self.db_table == "products": 
            form = "barcode"
        else: 
            form = "id"
        
        if self.db_table not in self.IS_DELETED_COL_ON:
            self.delete_item_from_db(self.db_table, "id", self.item_id)
        else:
            self.update_info(
                self.db_table,
                ["is_deleted"],
                (1,),
                f"{form} = ?",
                (self.item_id,)
            )
        
        self.qt_table.setRowCount(0)

        self.refresh_table()

    def delete_item(self):
        if self.item_id is None:
            self.select_item_warning()
        else:
            confirmation_msg = "هل أنت متأكد من عملية الحذف؟"
            form = ConfirmationMsgForm(ConfirmationMsgFormUi, confirmation_msg)
            form.confirmed.connect(self.on_delete_confirmed)
            form.exec()
            self.play_success_sound()

    def set_window_title(self, title): 
        self.setWindowTitle(title)
    
    def select_item_warning(self): 
        self.show_err_msg("قم بتحديد العنصر أولا")


   



        