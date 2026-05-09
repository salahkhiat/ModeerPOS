from .base_form import MainForm

from uis.database_ui import Ui_Form as DatabaseUi 
from .database_form import DatabaseForm

from uis.account import Ui_Form as AccountUi
from .account_form import AccountForm

from uis.analysis_tables import Ui_Form as AnalysisUi
from .analysis_form import AnalysisForm

from uis.mobile import Ui_Form as MobileUi
from .mobile_form import MobileForm

from uis.expense import Ui_Form as ExpenseUi 
from .expense_form import ExpenseForm

from uis.withdrawal import Ui_Form as WithdrawalUi 
from .withdrawal_form import WithdrawalForm

from uis.supplier_payment import Ui_Form as SupplierPaymentUi 
from .supplier_payment_form import SupplierPaymentForm

from uis.customer_payment import Ui_Form as CustomerPaymentUi 
from .customer_payment_form import CustomerPaymentForm

from uis.service import Ui_Form as ServiceUi
from .service_form import ServiceForm

from uis.invoice import Ui_Form as InvoiceUi 
from .invoice_form import InvoiceForm

from uis.services_table import Ui_ChooseItemUi as ServicesTableUi
from .services_table_form import ServicesTableForm

# We used 'category' UI for requested products form because it has the same required properties.
from uis.category import Ui_Form as RequestedProductUi
from .requested_product_form import RequestedProductForm

from uis.error_msg import Ui_Dialog as ErrorUi
from .error_form import ErrorForm

from uis.editable_items import Ui_ChooseItemUi as EditableItemsUi
from .editable_items_form import EditableItemsForm

from uis.pieces_transactions_table import Ui_ChooseItemUi as PiecesTransactionsUi
from .pieces_transactions_form import PiecesTransactionsForm

from uis.init_amount import Ui_Form as InitAmountUi
from .init_amount_form import InitAmountForm

from uis.show_table import Ui_ShowTableUi as ShowTableUi 
from .show_table_form import ShowTableForm

from .products_table_form import ProductsTableForm

from PyQt6.QtWidgets import (
    QTableWidget, 
    QHeaderView, 
    QSplashScreen, 
    QTableView, 
    QAbstractItemView,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from typing import Dict, List



import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class MainScreen(MainForm):
   
    def __init__(self,base_form):
        super().__init__(base_form)
        
        # preapare Database 
        self.prepare_database()

        # database auto backup
        self.db_auto_backup()
        
        # refresh main screentables
        db_timer = QTimer(self)
        db_timer.timeout.connect(self.db_auto_backup)
        db_timer.start(5000)
        
        # Set main screen title
        self.setWindowTitle("برنامج مدير لإدارة المحلات")
        
        # Set a main screen direction Right to Left
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Set screen icons
        self.set_screen_icons()

        # connect main screen buttons with their forms
        self.show_database_form()
        self.show_account_form()
        self.show_analysis_form()
        self.show_requested_product_form()
        self.show_mobile_form()
        self.show_expense_form()
        self.show_withdrawal_form()
        self.show_supplier_payment_form()
        self.show_customer_payment_form()
        self.show_service_form()
        self.add_customer_invoice_tab()
        self.show_supplier_invoice_tab()

        # opened customers invoices list
        self.opened_customers_invoices = []
        self.opened_suppliers_invoices = []

        # create settings.json file with default information if not exists.
        if not self.is_settings_file_exists():
            self.create_settings_file(self.get_settings_json_path())

        # if database path is not selected yet, open DatabaseForm
        settings = self.get_settings_info(self.get_settings_json_path())
        database = settings["database_path"]
        if database == None:
            form = DatabaseForm(DatabaseUi)
            form.exec()
        
        # Create the default  called "-"
        self.create_default_column("customers","name")
        self.create_default_column("services_categories","name")

        # refresh main screentables
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_main_screen_tables)
        timer.start(2500)

        # MenuBar
        users_header = ["المرجع", "الإسم", "الهاتف", "الحساب"]
        users_header_width: List[int] = [10, 30, 30, 30]
        users_db_table_cols = ["id", "name", "tel"]

        self.ui.suppliers_action.triggered.connect(
            lambda: self.show_tab(
                "جدول الموردين",
                "suppliers",
                users_db_table_cols,
                users_header,
                users_header_width
            )
        )
        self.ui.customers_action.triggered.connect(
            lambda: self.show_tab(
                "جدول الزبائن",
                "customers",
                users_db_table_cols,
                users_header,
                users_header_width
            )
        )
        self.ui.employees_action.triggered.connect(
            lambda: self.show_tab(
                "جدول الموظفين",
                "employees",
                users_db_table_cols,
                users_header,
                users_header_width
            )
        )

        products_header = ["المرجع", "الإسم", "الكمية", "البيع بـ", "الشراء بـ"]
        products_header_width = [15, 45, 10, 15, 15]
        products_db_table_cols = [
            "barcode", "name", "quantity", "sale_price", "purchase_price"
        ]

        self.ui.products_action.triggered.connect(
            lambda: self.show_tab(
                "جدول السلع", 
                "products", 
                products_db_table_cols, 
                products_header, 
                products_header_width
            )
        )

        needs_header = ["المعرف","وصف", "تاريخ الطلب"]
        needs_header_width = [15, 55, 30]
        needs_db_table_cols = ["id", "name", "created"]

        self.ui.needs_action.triggered.connect(
            lambda: self.show_tab(
                "جدول النقائص", 
                "requested_products", 
                needs_db_table_cols, 
                needs_header, 
                needs_header_width
            )
        )

        mobiles_header = [
            "ID", "موديل", "الشراء", "IMEI", "البائع", "رقم البائع", "تاريخ"
        ]
        mobiles_header_width = [5, 20, 10, 20, 20, 15, 10]
        mobiles_db_table_cols = [
            "id", "model", "price", "serial", "seller_name", "seller_tel", "created"
        ]

        self.ui.mobiles_action.triggered.connect(
            lambda: self.show_tab(
                "جدول الهواتف التي تم شرائها", 
                "mobiles", 
                mobiles_db_table_cols, 
                mobiles_header, 
                mobiles_header_width, 
            )
        )

        suppliers_transactions_header = [
            "المورد", "ملاحظة/فتورة", "عملية", "المبلغ", "التاريخ"
        ]
        suppliers_transactions_header_width = [15, 35, 12, 18, 20] #[20, 40, 10, 15, 15]

        suppliers_transactions_db_table_cols = [
            "name", 
            "note", 
            "_type", 
            "amount",
            "created"
        ]

        # I mixed between suppliers_transactions and suppliers tables.
        # s means suppliers, st means suppliers_transactions
        suppliers_transactions_db_table = "suppliers_transactions"
        self.ui.suppliers_deposits_action.triggered.connect(
            lambda: self.show_tab(
                "عمليات  الموردين", 
                suppliers_transactions_db_table, 
                suppliers_transactions_db_table_cols, 
                suppliers_transactions_header, 
                suppliers_transactions_header_width, 
            )
        )

        customers_payments_header = [
            "الزبون", "المصدر", "الوصف", "المبلغ", "التاريخ"
        ]
        customers_payments_header_width = [15, 12, 35, 18, 20]

        customers_money_columns = [
            "name",
            "process",
            "description",
            "amount",
            "created"
        ]
        # customers_transactions is a vertual table name 
        # it merged between there tables
        # services, customers_payments and sale_invoices
        customers_money_db_table = "customers_transactions"
        self.ui.customers_deposits_action.triggered.connect(
            lambda: self.show_tab(
                "عمليات  الزبائن", 
                customers_money_db_table, 
                customers_money_columns, 
                customers_payments_header, 
                customers_payments_header_width, 
            )
        )

        employees_withdrawals_header = [
            "العامل", "ملاحظة", "المبلغ", "التاريخ"
        ]
        employees_withdrawals_header_width = [25, 40, 15, 20]

        employees_withdrawals_columns = [
            "name",
            "note",
            "amount",
            "created"
        ]
        # employees_tansactions is a vertual table
        employees_withdrawals_db_table = "employees_transactions"
        self.ui.employees_withdrawals_action.triggered.connect(
            lambda: self.show_tab(
                "سحوبات العمال", 
                employees_withdrawals_db_table, 
                employees_withdrawals_columns, 
                employees_withdrawals_header, 
                employees_withdrawals_header_width, 
            )
        )

        expenses_header = [
            "ملاحظة", "الصنف", "المبلغ", "التاريخ"
        ]
        expenses_header_width = [25, 40, 15, 20]

        expenses_columns = [
            "note",
            "category",
            "amount",
            "created"
        ]
        # expenses is a real table but we used it as a vertual table
        expenses_db_table = "expenses"
        self.ui.expenses_action.triggered.connect(
            lambda: self.show_tab(
                "المصاريف", 
                expenses_db_table, 
                expenses_columns, 
                expenses_header, 
                expenses_header_width, 
            )
        )

        purchases_history_header = [
            "السلعة", "المرجع", "الشراء بـ", "الكمية", "المجموع", "الفاتورة", "التاريخ"
        ]
        purchases_history_header_width = [30, 12, 12, 7, 12, 12, 15 ]

        purchases_history_columns = [
            "name",
            "barcode",
            "price",
            "quantity",
            "total",
            "invoice",
            "created"
        ]
        # purchases_history is a real table but we used it as a vertual table
        purchases_history_db_table = "purchases_history"
        self.ui.purchases_history_action.triggered.connect(
            lambda: self.show_tab(
                "المشتريات", 
                purchases_history_db_table, 
                purchases_history_columns, 
                purchases_history_header, 
                purchases_history_header_width, 
            )
        )

        sales_history_header = [
            "السلعة", "المرجع", "البيع بـ", "الكمية", "المجموع", "الفاتورة", "التاريخ"
        ]
        sales_history_header_width = [25, 12, 12, 12, 12, 12, 15 ]

        sales_history_columns = [
            "name",
            "barcode",
            "price",
            "quantity",
            "total",
            "invoice",
            "created"
        ]
        # sales_history is a real table but we used it as a vertual table
        sales_history_db_table = "sales_history"
        self.ui.sales_history_action.triggered.connect(
            lambda: self.show_tab(
                "المبيعات", 
                sales_history_db_table, 
                sales_history_columns, 
                sales_history_header, 
                sales_history_header_width, 
            )
        )

        purchases_invoices_header = [
            "المورد", "مرجع الفاتورة", "المجموع", "الإيداع", "التاريخ"
        ]
        purchases_invoices_header_width = [35, 20, 15, 15, 15]

        purchases_invoices_columns = [
            "supplier", "inv_barcode", "total", "deposit", "created"
        ]
        # purchases_invoices is a real table but we used it as a vertual table
        purchases_invoices_db_table = "purchases_invoices"
        self.ui.purchases_invoices_action.triggered.connect(
            lambda: self.show_tab(
                "فواتير المشتريات", 
                purchases_invoices_db_table, 
                purchases_invoices_columns, 
                purchases_invoices_header, 
                purchases_invoices_header_width, 
            )
        )

        sales_invoices_header = [
            "الزبون", "مرجع الفاتورة", "المجموع", "الإيداع", "التاريخ"
        ]
        sales_invoices_header_width = [35, 20, 15, 15, 15]

        sales_invoices_columns = [
            "customer", "inv_barcode", "total", "deposit", "created"
        ]
        # sales_invoices is a real table but we used it as a vertual table
        sales_invoices_db_table = "sales_invoices"
        self.ui.sales_invoices_action.triggered.connect(
            lambda: self.show_tab(
                "فواتير البيع", 
                sales_invoices_db_table, 
                sales_invoices_columns, 
                sales_invoices_header, 
                sales_invoices_header_width, 
            )
        )

        services_header = [
            "الوصف", "الزبون", "الصنف", "السعر", "الإيداع", "التاريخ"
        ]
        services_header_width = [32, 18, 12, 12, 12, 14]

        services_columns = [
            "description", "customer", "category", "price", "paid", "created"
        ]
        # services is a real table but we used it as a vertual table
        services_db_table = "services"
        self.ui.services_action.triggered.connect(
            lambda: self.show_tab(
                "الخدمات", 
                services_db_table, 
                services_columns, 
                services_header, 
                services_header_width, 
                custom_form="services_table"
            )
        )

        services_categories_header = [
            "المعرف", "الصنف", "الخدمات", "الدخل"
        ]
        services_categories_header_width = [20, 40, 20, 20]

        services_categories_columns = [
            "id", "category", "services", "income"
        ]
        # services is a real table but we used it as a vertual table
        services_categories_db_table = "services_categories"
        self.ui.services_category_action.triggered.connect(
            lambda: self.show_tab(
                "أصناف الخدمات", 
                services_categories_db_table, 
                services_categories_columns, 
                services_categories_header, 
                services_categories_header_width, 
                
            )
        )

        expenses_categories_header = [
            "المعرف", "الصنف", "عملية", "المصروف"
        ]
        expenses_categories_header_width = [20, 40, 20, 20]

        expenses_categories_columns = [
            "id", "category", "expenses", "outcome"
        ]
        # expenses is a real table but we used it as a vertual table
        expenses_categories_db_table = "expenses_categories"
        self.ui.expenses_category_action.triggered.connect(
            lambda: self.show_tab(
                "أصناف المصروفات", 
                expenses_categories_db_table, 
                expenses_categories_columns, 
                expenses_categories_header, 
                expenses_categories_header_width, 
            )
        )

        # show tables view tabs
        self.ui.pieces_transactions_action.triggered.connect(self.show_pieces_transactions_tab)
        self.ui.init_amount_action.triggered.connect(self.show_init_amount_tab)

        ProductsTableForm(ShowTableUi)
        
        

    def refresh_main_screen_tables(self):
        self.refresh_requested_products_table()
        self.refresh_out_of_stock_table()
    # Welcome screen
    @staticmethod
    def show_welcome_screen(app, base_form_class, image_path="splash_screen.png", duration=3000, width=900, height=500):
        """
        Show a splash screen with a fixed size, then open MainScreen after `duration` ms.
        """
        # Load and scale the splash image
        splash_pix = QPixmap(image_path).scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # Create the splash
        splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()

        # Function to create and show main window after splash
        def show_main_window():
            window = MainScreen(base_form_class)
            
            window.showMaximized()
            splash.finish(window)
            window.play_failure_sound() # as welcome sound
            return window

        # Delay creation of main window
        QTimer.singleShot(duration, show_main_window)

        return splash
       
    # show tab table
    def show_tab(
            self, title: str, 
            db_table: str, 
            db_table_columns: List[str], 
            headers: List[str], 
            headers_width: List[int],
            font_size: int = 16,
            custom_form = None
    ) -> None:
        form = None 
        

        if custom_form is not None:
            if custom_form == "services_table":
                
                form = ServicesTableForm(ServicesTableUi) 
                form.exec() 

                
        else: 
            form = EditableItemsForm(EditableItemsUi) 
            form.set_window_title(title)
            
            # Table configuration
            table: QTableWidget = form.ui.table

            QTimer.singleShot(
                0, 
                lambda: self.set_table_properties(table, headers, headers_width)
            )
            form.set_db_table_info(
                table, db_table, db_table_columns, font_size=font_size
            )
            form.exec()
    
    # Show Pieces Transactions tab 
    def show_pieces_transactions_tab(self):
        form = PiecesTransactionsForm(PiecesTransactionsUi)
        form.exec()

    # Show Pieces Transactions tab 
    def show_init_amount_tab(self):
        form = InitAmountForm(InitAmountUi)
        form.exec()
    



    # set database form button 
    def database_form(self):
        form = DatabaseForm(DatabaseUi)
        form.exec()

    def show_database_form(self):
        self.ui.set_db_btn.clicked.connect(self.database_form)
    
    def requested_product_form(self):
        form = RequestedProductForm(RequestedProductUi)
        form.product_info.connect(self.refresh_requested_products_table)
        form.exec()
        
    def show_requested_product_form(self):
        self.ui.requested_products_btn.clicked.connect(self.requested_product_form)
    
    def refresh_requested_products_table(self,data:Dict=None):
        r_p_table:QTableWidget = self.ui.requested_products_table 
        r_p_table.setRowCount(0)
        self.remove_rows_counter(r_p_table)
        self.make_rows_scrollable(r_p_table)
        requested_products = None 
        if data is None:
            requested_products:Dict = self.get_table_as_dict("requested_products","name")
        else:
            requested_products = data
        header = r_p_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1,QHeaderView.ResizeMode.ResizeToContents)

        row = r_p_table.rowCount()

        for product in requested_products.values():
            r_p_table.insertRow(row)
            date_label = self.current_date()
            r_p_table.setItem(row, 0, self.make_item(product, read_only=True))
            r_p_table.setItem(row, 1, self.make_item(date_label, read_only=True)) 

    def refresh_out_of_stock_table(self):
        items = self.get_table_cols_list(
            "products",
            ["name","barcode","quantity","sale_price"],
            "quantity<6 AND is_deleted=0"
        )

        table_widget:QTableWidget = self.ui.out_of_stock_soon_table 
        table_widget.setRowCount(0)

        header = table_widget.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)         
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.remove_rows_counter(table_widget)
        self.make_rows_scrollable(table_widget)

        for item in items:
            # where the next row should go
            row = table_widget.rowCount() 
            
            # insert new row at the bottom of the table
            table_widget.insertRow(row) 
            for col_id, col_info in enumerate(item):
                    table_item = self.make_item(
                        col_info, font_size=16, read_only=True
                    )
                    table_widget.setItem(row, col_id, table_item)


    # set new user form button
    def account_form(self):
        form = AccountForm(AccountUi)
        form.exec()
    def show_account_form(self):
        self.ui.new_user_btn.clicked.connect(self.account_form)
    
    # set analysis form
    def analysis_form(self):
        form = AnalysisForm(AnalysisUi)
        form.exec()
    def show_analysis_form(self):
        self.ui.analysis_btn.clicked.connect(self.analysis_form)

    # set moblie buy mobile form
    def mobile_form(self):
        form = MobileForm(MobileUi)
        form.exec()
    def show_mobile_form(self):
        self.ui.buy_mobile_btn.clicked.connect(self.mobile_form)
    
    # set expenses form 
    def expense_form(self):
        form = ExpenseForm(ExpenseUi)
        form.exec()

    def show_expense_form(self):
        self.ui.new_expense_btn.clicked.connect(self.expense_form)

    # set withdrawal form 
    def withdrawal_form(self):
        form = WithdrawalForm(WithdrawalUi)
        form.exec()

    def show_withdrawal_form(self):
        self.ui.new_employee_withdrawal_btn.clicked.connect(self.withdrawal_form)
    
    # set supplier payment form 
    def supplier_payment_form(self):
        form = SupplierPaymentForm(SupplierPaymentUi)
        form.exec()

    def show_supplier_payment_form(self):
        self.ui.new_supplier_transaction_btn.clicked.connect(self.supplier_payment_form)

    # set customer payment form 
    def customer_payment_form(self):
        form = CustomerPaymentForm(CustomerPaymentUi)
        form.exec()
        
    def show_customer_payment_form(self):
        self.ui.new_customer_transaction_btn.clicked.connect(self.customer_payment_form)

    # set service form 
    def service_form(self):
        form = ServiceForm(ServiceUi)
        form.fetch_then_put("customers","name",form.ui.customer)
        form.fetch_then_put("services_categories","name",form.ui.category)
        form.exec()

    def show_service_form(self):
        self.ui.new_service_btn.clicked.connect(self.service_form)

    # add an invoice tab
    def add_invoice_tab(self,index_list,title,invoice_type=None):
                
                if len(index_list) < 3:
                    form = InvoiceForm(InvoiceUi,invoice_type) 
    
                    main_tab_widget = self.ui.tab_widget
                    # styling the active tab_bar
                    current_style = main_tab_widget.styleSheet()
                    new_style = "QTabBar::tab:selected {background-color:#3f5482;color:white;}"
                    main_tab_widget.setStyleSheet(current_style + "\n" + new_style)
                    # add a new tab 
                    tab_index = main_tab_widget.addTab(form,"")
                    # show it 
                    main_tab_widget.setCurrentIndex(tab_index)
                    # set its label
                    main_tab_widget.setTabText(tab_index,title )   
                    # add the tab invoice index to the opened inovices list 
                    index_list.append(tab_index)
                
                    # 🔑 Connect the cancel_btn to remove this tab
                    form.ui.cancel_btn.clicked.connect(lambda _, f=form: self.remove_tab_by_widget(f))

                    # ✅ Close tab when invoice is saved
                    form.invoice_saved.connect(lambda success, f=form: self.remove_tab_by_widget(f) if success else None)


                else:
                    print(f"You achieved the top, You have created {len(index_list)} Invoices")

    # remove an invoice tab index
    def remove_tab_index(self,target):
        if target in self.opened_customers_invoices:
            self.opened_customers_invoices.remove(target) 
            return True 
        
        elif target in self.opened_suppliers_invoices:
            self.opened_suppliers_invoices.remove(target)
            return True
        
        else:
            return False
        
    # remove an invoice tab
    def remove_tab_by_widget(self, widget):
        main_tab_widget = self.ui.tab_widget
        index = main_tab_widget.indexOf(widget)
        if index != -1:
            main_tab_widget.removeTab(index)
            self.remove_tab_index(index)
        
        self.refresh_out_of_stock_table()

    # set new customer invoice tab
    def customer_invoice_tab(self):
        self.add_invoice_tab(self.opened_customers_invoices,"فاتورة الزبون ","customers")

    def add_customer_invoice_tab(self):
        self.ui.new_customer_invoice_btn.clicked.connect(self.customer_invoice_tab)

    # set new supplier invoice tab
    def supplier_invoice_tab(self):
        # Are there suppliers 
        self.add_invoice_tab(self.opened_suppliers_invoices,"فاتورة المورد","suppliers")

    def show_supplier_invoice_tab(self):
        self.ui.new_supplier_invoice_btn.clicked.connect(self.supplier_invoice_tab)
    
    # Set Main Screen Icons
    def set_screen_icons(self):
        btns_icons = {
            "new_customer_invoice_btn":"add_a_sale_invoice.svg",
            "new_supplier_invoice_btn":"new_purchase_invoice.svg",
            "new_service_btn":"new_service.svg",
            "new_supplier_transaction_btn":"new_transaction_sup.svg",
            "new_customer_transaction_btn":"new_transaction_cus.svg",
            "new_employee_withdrawal_btn":"new_withdrawal.svg",
            "new_expense_btn":"new_expense.svg",
            "buy_mobile_btn":"buy_mobile.svg",
            "new_user_btn":"new_user.svg",
            "requested_products_btn":"requested_products.svg",
            "analysis_btn":"analysis.svg",
            "set_db_btn":"database.svg"
        }
        
        for btn, icon in btns_icons.items():
            self.set_icon(btn,icon)



        
