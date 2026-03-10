from PyQt6.QtWidgets import QHeaderView, QTableWidget, QPushButton, QLabel
from .base_form import Form

class AnalysisForm(Form):
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("إحصائيات المعاملات")
        # set icon
        self.set_icon("switch_analysis_btn","refresh.svg")
        self.analysis_time = "today"
        self.get_analysis()
        switch_btn:QPushButton = self.ui.switch_analysis_btn
        switch_btn.clicked.connect(self.switch_analysis_time)

    def switch_analysis_time(self):
        title_label: QLabel = self.ui.analysis_title
        expenses_table:QTableWidget = self.ui.expenses_table
        incomes_table:QTableWidget = self.ui.incomes_table
        expenses_table.setRowCount(0)
        incomes_table.setRowCount(0)
        if self.analysis_time == "today":
            self.analysis_time = "month"
            title_label.setText("إحصائيات الشهر")
        elif self.analysis_time == "month":
            self.analysis_time = "today"
            title_label.setText("إحصائيات اليوم")

        self.get_analysis(self.analysis_time)
        

    def get_analysis(self, s_date:str="today"):
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
        sales_cash = self.get_sales_cash(s_date)
        
        services_cash = self.get_services_cash(s_date)

        customers_cash = self.get_customers_cash(s_date)

        cash = float(sales_cash) + float(services_cash) + float(customers_cash)

        sales_capital = self.get_sales_capital(s_date)
        sales_profit = sales_cash - sales_capital
        # profits = sales_profit + services_cash
        self.remove_rows_counter(incomes_table)
        self.make_rows_scrollable(incomes_table)

        row = incomes_table.rowCount()

        incomes_table.insertRow(row)
        cash_label = "الدخل الإجمالي"
        incomes_table.setItem(row, 0, self.make_item(cash_label, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{cash:.2f}", color="green", read_only=True))

        incomes_table.insertRow(row)
        customers_cash_label = "إيداعات الزبائن"
        incomes_table.setItem(row, 0, self.make_item(customers_cash_label, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{customers_cash:.2f}", read_only=True))
        
        incomes_table.insertRow(row)
        services_cash_label = "الخدمات"
        incomes_table.setItem(row, 0, self.make_item(services_cash_label, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{cash:.2f}", read_only=True))

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

        expenses = self.get_expenses(s_date)
        purchases_deposits = self.get_purchases_deposits(s_date)

        suppliers_deposits = self.get_suppliers_deposits(s_date)

        suppliers_debts = self.get_suppliers_debts(s_date)

        employees_withdrawals = self.get_employees_withdrawals(s_date)

        suppliers_new_debts = suppliers_debts - suppliers_deposits

        outcome = expenses + suppliers_deposits + purchases_deposits + employees_withdrawals 

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


        # cunclution 
        net_result = cash - outcome

        incomes_table.insertRow(row)
        net_result_label = "الصافي"
        color = "green"
        if net_result < 0:
            color = "red"
        incomes_table.setItem(row, 0, self.make_item(net_result_label, color=color, read_only=True))
        incomes_table.setItem(row, 1, self.make_item(f"{net_result:.2f}", color=color, read_only=True))







        
       


