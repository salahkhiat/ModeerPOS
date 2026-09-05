from .base_form import Form
from PyQt6.QtWidgets import (
    QTableView, 
    QHeaderView, 
    QMessageBox,
)
from .shared_functions import TableViewModel

from uis.confirmation_msg import Ui_Dialog as ConfirmationMsgUi
from .confirmation_msg_form import ConfirmationMsgForm

from uis.service import Ui_Form as ServiceUi
from .service_form import ServiceForm

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ServicesTableForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)

        self.setWindowTitle("سجل الخدمات التي تم تقديمها")

        # set icons
        self.set_icons()

        # Pagination part
        next_btn = self.ui.next_btn
        previous_btn = self.ui.previous_btn
        
        next_btn.clicked.connect(self.next_page)
        previous_btn.clicked.connect(self.previous_page)

        self.page = 0
        self.page_size = 15
        self.pagination_counter = self.ui.page_number

        # load table 
        self.columns_header = [
            "معرف","جهاز", "موديل", "زبون", "صنف", "سعر", "دفع", "التاريخ"
        ]
        self.keyword = None 
        self.load_table()

        # Search box
        search_box = self.ui.search_box
        search_box.textChanged.connect(self.load_table)

        # Buttons
        self.connect_buttons()
    
    def on_row_selected(self, selected, deselected):
        indexes = selected.indexes()
        
        if indexes:
            row = indexes[0].row()
            self.selected_service_row = self.model._data[row]
       

    def load_table(self, keyword=None):
        
        keyword = str(keyword).strip() if keyword is not None else None

        # 🔥 only reset page if keyword CHANGED
        if keyword != self.keyword:
            self.page = 0

        self.keyword = keyword
                 
        table: QTableView = self.ui.table
        
        offset = self.page * self.page_size
        
        data = self.get_services_list(keyword=keyword, limit=self.page_size, offset=offset)
        
        
        self.model = TableViewModel(data, self.columns_header)
        table.setModel(None)
        table.setModel(self.model)

        self.set_table_basic_settings(table)

        # 🔥 update pagination counter
        self.update_pagination_counter() 

        self.selected_service_row = None

        # selected model
        selection_model = table.selectionModel()
        selection_model.selectionChanged.connect(self.on_row_selected)  
    
    # def on_row_selected(self, selected, deselected):
    #     indexes = selected.indexes()
        
    #     if indexes:
    #         row = indexes[0].row()
    #         self.selected_service_row = self.model._data[row]

    def next_page(self):
        self.page += 1
        data = self.get_services_list(keyword=self.keyword, limit=self.page_size, offset=self.page * self.page_size)

        if not data:
            self.page -= 1  # rollback
            return

        self.load_table(keyword=self.keyword)

    def previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_table(keyword=self.keyword)
    
    def set_table_view_headers(
            self, 
            table, 
            fixed_cols:dict[int:int], 
            resize_to_content_col:int, 
            stretch_col:int
        ):
        """ Set A table view headers, columns fixed and stretch widths"""

        header = table.horizontalHeader()
        col_count = table.model().columnCount()

        # Set all to Interactive first
        for col in fixed_cols.keys():
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        for col, width in fixed_cols.items():
            # Custom widths for first col
            table.setColumnWidth(col, width)
        
        if resize_to_content_col:
            header.setSectionResizeMode(resize_to_content_col, QHeaderView.ResizeMode.ResizeToContents)

        # Last column stretches
        header.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)

    def set_table_basic_settings(self, table):
        # Set table view headers and columns
        cols_widths = { 1:100, 3:140 ,4:120, 5:90, 6:90, 7:180 }
        stretch_col = 2
        resize_to_content_col = 0
        self.set_table_view_headers(table, cols_widths, resize_to_content_col, stretch_col)

        # make a row scrollable
        self.remove_rows_counter(table)
        self.make_rows_scrollable(table)

    def update_pagination_counter(self):
        current_page_number = self.page + 1
        # this line prevent my table to appears 
        self.pagination_counter.setText(f"{current_page_number}")

    def set_icons(self):
        self.set_icon("delete_btn","delete.svg")
        self.set_icon("add_btn","add.svg")
        self.set_icon("previous_btn","previous.svg")
        self.set_icon("next_btn","next.svg")
        self.set_icon("cancel_btn","cancel.svg")

    def delete_btn_clicked(self):
        self.ui.delete_btn.clicked.connect(self.delete_service)
    
    def add_btn_clicked(self):
        self.ui.add_btn.clicked.connect(self.add_service)

    def delete_service(self):
        if self.selected_service_row is None:
            title = "تأكيد عمية الحذف"
            text = "إختر الخدمة التي تريد حذفها"
            QMessageBox.warning(None, title, text)
        else:
            msg = "هل أنت متأكد من عملية الحذف؟"
            form = ConfirmationMsgForm(ConfirmationMsgUi, msg)
            form.confirmed.connect(self.confirm_deletion)
            form.exec()
        
    def add_service(self):
        form = ServiceForm(ServiceUi)
        form.fetch_then_put("customers","name",form.ui.customer)
        form.fetch_then_put("services_categories","name",form.ui.category)
        form.exec()
        
        # Reset pagination
        self.page = 0 

        # Reload table
        self.load_table()

    def confirm_deletion(self, cmd):
        if cmd is True:
            # Get the selected service id.
            service_id = self.selected_service_row[0]
            
            # Delete the selected service.
            self.delete_item_from_db("services", "id", service_id)

            # Reset the pagination page to 0.
            self.page = 0 

            # Reload the services table.
            self.load_table()

    def connect_buttons(self):
        self.add_btn_clicked()
        self.delete_btn_clicked()
    

    





        