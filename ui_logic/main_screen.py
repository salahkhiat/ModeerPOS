from .base_form import MainForm
from uis.database_ui import Ui_Form as DatabaseUi 
from .database_form import DatabaseForm

from uis.account import Ui_Form as AccountUi
from .account_form import AccountForm

from uis.analysis_tables import Ui_Form as AnalysisUi
from .analysis_form import AnalysisForm


from uis.activation import Ui_Dialog as ActivationUi
from .activation_form import ActivationForm

from .show_main_tables import ShowMainTables

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

from uis.editable_items import Ui_ChooseItemUi as EditableItemsUi
from .editable_items_form import EditableItemsForm

from uis.pieces_transactions_table import Ui_ChooseItemUi as PiecesTransactionsUi
from .pieces_transactions_form import PiecesTransactionsForm

from uis.init_amount import Ui_Form as InitAmountUi
from .init_amount_form import InitAmountForm

from uis.show_table import Ui_ShowTableUi as ShowTableUi 

from .products_table_form import ProductsTableForm
from .suppliers_transactions_table_form import SuppliersTransactionsTableForm
from .customers_payments_table_form import CustomersPaymentsTableForm
from .employees_withdrawals_table_form import EmployeesWithdrawalsTableForm
from .expenses_table_form import ExpensesTableForm
from .purchases_history_table_form import PurchasesHistoryTableForm
from .purchases_invoices_table_form import PurchasesInvoicesTableForm
from .sales_history_table_form import SalesHistoryTableForm
from .sales_invoices_table_form import SalesInvoicesTableForm
from uis.support import Ui_Dialog as SupportUi
from .support_form import SupportForm


from PyQt6.QtWidgets import QTableWidget, QSplashScreen 
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from typing import List



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
        self.setWindowTitle("مدير : البساطة في إدارة المحلات")
        
        # Set a main screen direction Right to Left
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Set screen icons
        self.set_screen_icons()

        # connect main screen buttons with their forms
        self.show_database_form()
        self.show_account_form()
        self.show_analysis_form()
        self.show_requested_product_form()
        self.show_support_form()
        self.show_expense_form()
        self.show_withdrawal_form()
        self.show_supplier_payment_form()
        self.show_customer_payment_form()
        self.show_service_form()
        self.add_customer_invoice_tab()
        self.show_supplier_invoice_tab()

        # set main tables with TableView
        requested_products_table = self.ui.requested_products_table
        req_pro_counter = self.ui.page_counter_1
        req_pro_next_btn = self.ui.next_page_1_btn
        req_pro_previous_btn = self.ui.previous_page_1_btn

        self.requested_products_table_manager = ShowMainTables(
            requested_products_table,
            self.get_requested_products_list,
            ["المعرف", "الإسم"],
            None,
            1,
            0,
            req_pro_next_btn,
            req_pro_previous_btn,
            req_pro_counter
        )
        out_of_stock_table = self.ui.out_of_stock_soon_table
        out_of_stock_counter = self.ui.page_counter_2
        out_of_stock_next_btn = self.ui.next_page_2_btn
        out_of_stock_previous_btn = self.ui.previous_page_2_btn

        self.out_of_stock_table_manager = ShowMainTables(
            out_of_stock_table,
            self.get_out_of_stock_list,
            ["الإسم", "الباركود", "الكمية", "البيع بـ"],
            None,
            0,
            1,
            out_of_stock_next_btn,
            out_of_stock_previous_btn,
            out_of_stock_counter
        )
        
        # refresh main screentables
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_main_screen_tables)
        timer.start(2500)

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
        self.ui.activation_action.triggered.connect(self.show_activation_tab)

        self.ui.products_action.triggered.connect(self.show_products_table_tab)
        self.ui.suppliers_deposits_action.triggered.connect(self.show_suppliers_transactions_table_tab)
        self.ui.customers_deposits_action.triggered.connect(self.show_customers_payments_table_tab)

        self.ui.employees_withdrawals_action.triggered.connect(self.show_employees_withdrawals_table_tab)
        self.ui.expenses_action.triggered.connect(self.show_expenses_table_tab)
        self.ui.purchases_history_action.triggered.connect(self.show_purchases_history_table_tab)
        self.ui.purchases_invoices_action.triggered.connect(self.show_purchases_invoices_table_tab)
        self.ui.sales_history_action.triggered.connect(self.show_sales_history_table_tab)
        self.ui.sales_invoices_action.triggered.connect(self.show_sales_invoices_table_tab)

    def refresh_main_screen_tables(self):
        self.requested_products_table_manager.load_table()
        self.out_of_stock_table_manager.load_table()
        
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
       
    # Show tabs 
    def show_products_table_tab(self):
        ProductsTableForm(ShowTableUi)

    def show_suppliers_transactions_table_tab(self):
        SuppliersTransactionsTableForm(ShowTableUi)

    def show_customers_payments_table_tab(self):
        CustomersPaymentsTableForm(ShowTableUi)

    def show_employees_withdrawals_table_tab(self):
        EmployeesWithdrawalsTableForm(ShowTableUi) 

    def show_expenses_table_tab(self):
        ExpensesTableForm(ShowTableUi)

    def show_purchases_history_table_tab(self):
        PurchasesHistoryTableForm(ShowTableUi)

    def show_purchases_invoices_table_tab(self):
        PurchasesInvoicesTableForm(ShowTableUi)

    def show_sales_history_table_tab(self):
        SalesHistoryTableForm(ShowTableUi)

    def show_sales_invoices_table_tab(self):
        SalesInvoicesTableForm(ShowTableUi)

    def show_activation_tab(self):
        form = ActivationForm(ActivationUi)
        form.exec()

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
        form.exec()
        
    def show_requested_product_form(self):
        self.ui.requested_products_btn.clicked.connect(self.requested_product_form)
    
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
    def support_form(self):
        form = SupportForm(SupportUi)
        form.exec()

    def show_support_form(self):
        self.ui.support_btn.clicked.connect(self.support_form)
    
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
        
        self.out_of_stock_table_manager.load_table()

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
            "support_btn":"support.svg",
            "new_user_btn":"new_user.svg",
            "requested_products_btn":"requested_products.svg",
            "analysis_btn":"analysis.svg",
            "set_db_btn":"database.svg",
            "next_page_1_btn": "next.svg",
            "next_page_2_btn": "next.svg",
            "previous_page_1_btn": "previous.svg",
            "previous_page_2_btn": "previous.svg"
        }
        
        for btn, icon in btns_icons.items():
            self.set_icon(btn,icon)



        
