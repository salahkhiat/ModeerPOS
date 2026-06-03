from PyQt6.QtWidgets import QHeaderView, QTableWidget, QPushButton, QLabel, QComboBox
from .base_form import Form
import logging
import json
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class AnalysisForm(Form):
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("إحصائيات المعاملات")
        # set icon
        self.set_icon("switch_analysis_btn","refresh.svg")
        self.set_icon("search_btn","apply.svg")
        self.analysis_time = "today"
        self.get_analysis()
        switch_btn:QPushButton = self.ui.switch_analysis_btn
        switch_btn.clicked.connect(self.switch_analysis_time)

        search_btn: QPushButton = self.ui.search_btn
        search_btn.clicked.connect(self.get_selected_date_analysis)
        

    def get_box_money(self) -> float:
        """ The box money in the beginning of the day"""
        settings_path = self.get_settings_json_path()

        # Load the JSON file
        with open(settings_path, "r") as file:
            data = json.load(file)

        return float(data["init_amount"])
        

    def get_selected_date(self) -> str:
        year: QComboBox = self.ui.year.currentText()
        months = {
            0: '01', 1:'02', 2:'03', 3:'04', 4:'05', 5:'06', 
            6:'07', 7:'08', 8:'09', 9:'10', 10:'11', 11:'12'
        }
        month_index: QComboBox = self.ui.month.currentIndex()
        return f"{year}-{months[month_index]}"

    
    def get_selected_date_analysis(self):
        selected_date = self.get_selected_date()

        title_label: QLabel = self.ui.analysis_title
        title_label.setText(f"{selected_date}")

        self.clean_analysis_table()
        self.get_analysis("month", selected_date)

    def clean_analysis_table(self):
        expenses_table:QTableWidget = self.ui.expenses_table
        incomes_table:QTableWidget = self.ui.incomes_table
        expenses_table.setRowCount(0)
        incomes_table.setRowCount(0)

    def switch_analysis_time(self):
        title_label: QLabel = self.ui.analysis_title
        self.clean_analysis_table()

        if self.analysis_time == "today":
            self.analysis_time = "month"
            title_label.setText("إحصائيات الشهر")

        elif self.analysis_time == "month":
            self.analysis_time = "today"
            title_label.setText("إحصائيات اليوم")
        
        self.get_analysis(self.analysis_time)
        

    def get_analysis(self, s_date:str="today", specific_date=None):
        """ Getting analysis depending on search date or s_date 'today' or 'month' """

        # incomes
        incomes_table: QTableWidget = self.ui.incomes_table
            # headers
        header = incomes_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        incomes_table.setColumnWidth(0, 240)
        # incomes_table.verticalHeader().setDefaultSectionSize(55)
        incomes_table.verticalHeader().setDefaultSectionSize(45)
        # CASH PART HAS STARTED
        sales_cash = self.get_sales_cash(s_date, specific_date)

        services_cash = self.get_services_cash(s_date, specific_date)

        customers_cash = self.get_customers_cash(s_date, specific_date)
        
        cash = float(sales_cash) + float(services_cash) + float(customers_cash)

        if s_date == "today":
            cash += self.get_box_money()

        services_profits = self.get_services_profits(s_date, specific_date)

        sales_capital = self.get_sales_capital(s_date, specific_date)

        sales = self.get_sales_pure(s_date, specific_date)
        sales_profits = sales - sales_capital

        profits = sales_profits + services_profits
       
        self.remove_rows_counter(incomes_table)
        
        self.make_rows_scrollable(incomes_table)
        
        row = incomes_table.rowCount()
       
        incomes_table.insertRow(row)
        profits_label = "الربح "
        incomes_table.setItem(row, 0, self.make_item(profits_label, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{profits:.2f}", color="green", read_only=True))

        incomes_table.insertRow(row)
        cash_label = "الدخل "
        if s_date == "today":
            cash_label = "الدخل + مبلغ البداية"
        incomes_table.setItem(row, 0, self.make_item(cash_label, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{cash:.2f}", color="green", read_only=True))

        # incomes_table.insertRow(row)
        # customers_cash_label = "إيداعات الزبائن"
        # incomes_table.setItem(row, 0, self.make_item(customers_cash_label, read_only=True))
        # incomes_table.setItem(row, 1, self.make_item(f"{customers_cash:.2f}", read_only=True))

        
        # incomes_table.insertRow(row)
        # services_profits_label = "أرباح الخدمات"
        # incomes_table.setItem(row, 0, self.make_item(services_profits_label, read_only=True))
        # incomes_table.setItem(row, 1, self.make_item(f"{services_profits:.2f}", read_only=True))
        
        incomes_table.insertRow(row)
        services_cash_label = "الخدمات"
        incomes_table.setItem(row, 0, self.make_item(services_cash_label, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{services_cash:.2f}", read_only=True))


        # incomes_table.insertRow(row)
        # sales_profits_label = "أرباح المبيعات"
        # incomes_table.setItem(row, 0, self.make_item(sales_profits_label, read_only=True))
        # incomes_table.setItem(row, 1, self.make_item(f"{sales_profits:.2f}", read_only=True))

        incomes_table.insertRow(row)
        sales_cash_label = "المبيعات"
        incomes_table.setItem(row, 0, self.make_item(sales_cash_label, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{sales_cash:.2f}", read_only=True))

        # incomes_table.insertRow(row)
        # profits_label = "الربح الإجمالي "
        # incomes_table.setItem(row, 0, self.make_item(profits_label,color="green"))
        # incomes_table.setItem(row, 1, self.make_item(f"{profits:.2f}",color="green"))
        
        # incomes_table.insertRow(row)
        # cus_pay_label = " إداعات الزبون المميز"
        # incomes_table.setItem(row, 0, self.make_item(cus_pay_label))
        # incomes_table.setItem(row, 1, self.make_item(f"{customers_cash:.2f}"))

        # incomes_table.insertRow(row)
        # services_label = "أرباح الخدمات "
        # incomes_table.setItem(row, 0, self.make_item(services_label))
        # incomes_table.setItem(row, 1, self.make_item(f"{services_cash:.2f}"))

        # incomes_table.insertRow(row)
        # sales_profit_label = "أرباح السلع"
        # incomes_table.setItem(row, 0, self.make_item(sales_profit_label))
        # incomes_table.setItem(row, 1, self.make_item(f"{sales_profit:.2f}"))

        # incomes_table.insertRow(row)
        # capital_label = "رأس مال المبيعات"
        # incomes_table.setItem(row, 0, self.make_item(capital_label))
        # incomes_table.setItem(row, 1, self.make_item(f"{sales_capital:.2f}"))

        # OUTCOME PART HAS STARTED
        expenses_table: QTableWidget = self.ui.expenses_table
        ex_header = expenses_table.horizontalHeader()
        ex_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        expenses_table.setColumnWidth(0, 250)
        expenses_table.verticalHeader().setDefaultSectionSize(45)

        self.remove_rows_counter(expenses_table)
        row = expenses_table.rowCount()

        expenses = self.get_expenses(s_date, specific_date)

        purchases_deposits = self.get_purchases_deposits(s_date, specific_date)

        suppliers_deposits = self.get_suppliers_deposits(s_date, specific_date)

        suppliers_debts = self.get_suppliers_debts(s_date, specific_date)

        employees_withdrawals = self.get_employees_withdrawals(s_date, specific_date)

        # suppliers_new_debts = suppliers_debts - suppliers_deposits

        outcome = expenses + suppliers_deposits + employees_withdrawals 

        expenses_table.insertRow(row)
        total_ex_label = "الخرج الإجمالي"
        expenses_table.setItem(row, 0, self.make_item(total_ex_label, read_only=True))
        expenses_table.setItem(row, 1, self.make_item(f"{outcome:.2f}", color="red", read_only=True))

        expenses_table.insertRow(row)
        ex_label = " مصاريف عامة"
        expenses_table.setItem(row, 0, self.make_item(ex_label, read_only=True))
        expenses_table.setItem(row, 1, self.make_item(f"{expenses:.2f}", read_only=True))

        expenses_table.insertRow(row)
        purchases_deposits_label = "مشتريات سلع"
        expenses_table.setItem(row, 0, self.make_item(purchases_deposits_label, read_only=True))
        expenses_table.setItem(row, 1, self.make_item(f"{purchases_deposits:.2f}", read_only=True))

        expenses_table.insertRow(row)
        suppliers_deposits_label = "إيداعاتي للموردين"
        expenses_table.setItem(row, 0, self.make_item(suppliers_deposits_label, read_only=True))
        expenses_table.setItem(row, 1, self.make_item(f"{suppliers_deposits:.2f}", read_only=True))

        expenses_table.insertRow(row)
        employees_withdrawals_label = "سحوبات  العمال "
        expenses_table.setItem(row, 0, self.make_item(employees_withdrawals_label, read_only=True))
        expenses_table.setItem(row, 1, self.make_item(f"{employees_withdrawals:.2f}", read_only=True))

        # expenses_table.insertRow(row)
        # suppliers_new_debts_label = "دين جديد - الموردين"
        # expenses_table.setItem(row, 0, self.make_item(suppliers_new_debts_label))
        # expenses_table.setItem(row, 1, self.make_item(f"{suppliers_new_debts:.2f}"))










        
       


