from .base_form import Form
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QHeaderView
from .shared_functions import TableViewModel

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class PiecesTransactionsForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set icons
        self.set_icons()

        # Pagination part
        next_btn = self.ui.next_btn
        previous_btn = self.ui.previous_btn
        
        next_btn.clicked.connect(self.next_page)
        previous_btn.clicked.connect(self.previous_page)

        self.page = 0
        self.page_size = 3 
        self.pagination_counter = self.ui.pagination_label

        # load table 
        self.columns_header = ["المعرف", "المورد", "القطعة", "السعر", "الحالة", "التاريخ"]
        self.load_table()


        # # Get selected row data
        # index = table.currentIndex()
        # row = index.row()
        # print("Selected row:", row)
        # print("Data:", model._data[row])





    def load_table(self):
        table: QTableView = self.ui.table
        
        offset = self.page * self.page_size
        
        data = self.get_pieces_transactions_list(limit=self.page_size, offset=offset)
        model = TableViewModel(data, self.columns_header)

        table.setModel(model)

        self.set_table_basic_settings(table)

        # 🔥 update pagination counter
        self.update_pagination_counter()


    def next_page(self):
        self.page += 1
        data = self.get_pieces_transactions_list(limit=self.page_size, offset=self.page * self.page_size)

        if not data:
            self.page -= 1  # rollback
            return

        self.load_table()

    def previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_table()
    
    def set_table_basic_settings(self, table):
        # Make the content fits the full width
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # make a row scrollable
        self.remove_rows_counter(table)
        self.make_rows_scrollable(table)

    def update_pagination_counter(self):
        current_page_number = self.page + 1
        # this line prevent my table to appears 
        self.pagination_counter.setText(f"{current_page_number}")

    def set_icons(self):
        self.set_icon("install_btn","install.svg")
        self.set_icon("in_shop_btn","pending.svg")
        self.set_icon("return_btn","return.svg")
        self.set_icon("delete_btn","delete.svg")
        self.set_icon("previous_btn","previous.svg")
        self.set_icon("next_btn","next.svg")
        self.set_icon("cancel_btn","cancel.svg")
         


        