from .base_form import Form
from .show_table_form import ShowTableForm

from uis.customer_payment import Ui_Form as CustomersPaymentsUi
from .customer_payment_form import CustomerPaymentForm

from uis.service import Ui_Form as ServiceUi
from .service_form import ServiceForm

from PyQt6.QtWidgets import QMessageBox
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class CustomersPaymentsTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)

        self.form = ShowTableForm(
            base_form,
            "سجل إيداعات الزبائن ",
            "customers_payments",
            self.get_customers_transactions_list,
            ["المعرف", "الزبون", "الوصف" ,"العملية",  "الإيداع", "التاريخ"],
            {1:100, 3:100, 4:100, 5:180 },
            2,
            0,
            "id"
        ) 
        self.form.ui.edit_btn.clicked.connect(self.edit_transaction)
        


        self.form.exec()

    def change_db_table(self):
        transaction = self.form.selected_row
        process = transaction[3]
        db_tables = {
            "payment": "customers_payments",
            "service": "services"
        }
        self.form._db_table = db_tables[process]
        
    
    def edit_transaction(self):

        transaction = self.form.selected_row

        if transaction is None:
            QMessageBox.warning(None, "تنبيه", "لم تحدد أي معاملة بعد")

        else:
            
            transaction_id = transaction[0]
            customer_name = transaction[1]
            description = transaction[2]
            process = transaction[3]
            amount = transaction[4]
            
            if process == "payment":
                form = CustomerPaymentForm(CustomersPaymentsUi, transaction_id, customer_name)
                form.ui.amount.setText(str(amount))
                form.ui.note.setText(str(description))
                form.payment_updated.connect(lambda _ : self.form.load_table())
                form.exec()

            elif process == "service":
                columns = ("category_id", "description", "default_price", "paid_price", "piece_price" )
                service = self.get_item_info("services", columns, "id", transaction_id)
                
                category = self.get_item_info("services_categories", ("name",), "id", service['category_id'])
                
                form = ServiceForm(ServiceUi, transaction_id, customer_name, category['name'])
                
                form.ui.note.setText(str(service['description']))
                if float(service['paid_price']) > 0:
                    form.ui.deposit.setEnabled(True)
                    form.ui.deposit.setStyleSheet("background:white")
                form.ui.deposit.setText(str(service['paid_price']))
                form.ui.amount.setText(str(service['default_price']))
                form.ui.piece_price.setText(str(service['piece_price']))
                form.exec()

            elif process == "sale":
                QMessageBox.warning(None, "تنبيه", "لا يمكنك التعديل على عملية البيع من هنا") 

            else:
                pass 


        

        


        