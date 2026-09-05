from .base_form import Form
from PyQt6.QtWidgets import (
    QTableView, 
    QHeaderView, 
    QMessageBox,
    QComboBox
)
from .shared_functions import TableViewModel

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class PiecesTransactionsForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)

        self.setWindowTitle("سجل حالة قطع غيار الصيانة")

        # set icons
        self.set_icons()
       
        # Pagination part
        next_btn = self.ui.next_btn
        previous_btn = self.ui.previous_btn
        
        next_btn.clicked.connect(self.next_page)
        previous_btn.clicked.connect(self.previous_page)

        self.page = 0
        self.page_size = 15
        self.pagination_counter = self.ui.pagination_label
        
        # load table 
        self.columns_header = ["المعرف", "المورد", "القطعة", "السعر", "الحالة", "التاريخ"]
        self.keyword = None
        
        self.load_table()
        
        
        # connect buttons
        self.connect_buttons()
        
        # status combo
        status: QComboBox = self.ui.status_type
        status.currentIndexChanged.connect(self.show_current_combo)
        
        # Search box
        search_box = self.ui.search_box
        search_box.textChanged.connect(
            lambda box_keyword : self.load_table(keyword=box_keyword)
        )

    def show_current_combo(self):
        status: QComboBox = self.ui.status_type
        status_list = {
            0: None,
            1:"in_shop",
            2:"installed",
            3:"returned"
        }
        selected_status = status_list[status.currentIndex()]
        
        # load the table
        self.load_table(status_type=selected_status)


    def load_table(self, status_type=None, keyword=None):
        
        keyword = str(keyword).strip() if keyword is not None else None
        
        # 🔥 only reset page if keyword CHANGED
        if keyword != self.keyword:
            self.page = 0

        self.keyword = keyword
        
        table: QTableView = self.ui.table
        
        offset = self.page * self.page_size
        
        data = self.get_pieces_transactions_list(
            keyword=keyword, 
            status=status_type, 
            limit=self.page_size, 
            offset=offset
        )
        
        self.model = TableViewModel(data, self.columns_header)
        
        table.setModel(self.model)
        
        self.set_table_basic_settings(table)
       

        # 🔥 update pagination counter
        self.update_pagination_counter()

        self.selected_piece_row = None

        # selected model
        selection_model = table.selectionModel()
        selection_model.selectionChanged.connect(self.on_row_selected)  
    
    def on_row_selected(self, selected, deselected):
        indexes = selected.indexes()
        
        if indexes:
            row = indexes[0].row()
            self.selected_piece_row = self.model._data[row]

    def next_page(self):
        self.page += 1
        data = self.get_pieces_transactions_list(keyword=self.keyword, limit=self.page_size, offset=self.page * self.page_size)

        if not data:
            self.page -= 1  # rollback
            return

        self.load_table(keyword=self.keyword)

    def previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_table(keyword=self.keyword)
    
    def set_table_view_headers(self, table:QTableView, fixed_cols:dict[int:int], stretch_col:int):
        """ Set A table view headers, columns fixed and stretch widths"""
        
        header:QHeaderView = table.horizontalHeader()
      
        # Set all to Interactive first
        for col in fixed_cols.keys():
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        
        for col, width in fixed_cols.items():
            # Custom widths for first col
            table.setColumnWidth(col, width)
        
        # Last column stretches
        header.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)

    def set_table_basic_settings(self, table:QTableView):
        # Set table view headers and columns
        
        cols_widths = {0:80, 1:150, 3:100, 4:85, 5:180}
        stretch_col = 2
        
        self.set_table_view_headers(table, cols_widths, stretch_col)
        
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
    
    def connect_buttons(self):
        self.install_btn_clicked()
        self.return_btn_clicked()
        self.in_shop_btn_clicked()
        self.delete_btn_clicked()
    
    def update_piece_status(self, status:str):
        table = "pieces_transactions"
        columns = ["status", "created"]
        data = (status, self.current_date())
        id = self.selected_piece_row[0]
        self.update_info(table, columns, data, "id=?", (id,))
        self.load_table()

    def set_piece_installed(self):
        
        if self.selected_piece_row is not None:
            self.update_piece_status("installed")
            QMessageBox.warning(None, "حالة القطعة", "تم تركيب القطعة بنجاح")
        else:
            logger.warning("No row selected yet")
    
    def install_btn_clicked(self):
        self.ui.install_btn.clicked.connect(self.set_piece_installed)

    def set_piece_in_shop(self):
        if self.selected_piece_row is not None:
            self.update_piece_status("in_shop")
        else:
            logger.warning("No row selected yet")
    
    def in_shop_btn_clicked(self):
        self.ui.in_shop_btn.clicked.connect(self.set_piece_in_shop)

    def set_piece_returned(self):
        if self.selected_piece_row is not None:
            self.update_piece_status("returned")
        else:
            logger.warning("No row selected yet")
    
    def return_btn_clicked(self):
        self.ui.return_btn.clicked.connect(self.set_piece_returned)

    def set_piece_deleted(self):
        if self.selected_piece_row is not None:
            id = self.selected_piece_row[0]
            table = "pieces_transactions"
            self.delete_item_from_db(table, "id",id)
            self.load_table()
        else:
            logger.warning("No row selected yet")
        
    def delete_btn_clicked(self):
        self.ui.delete_btn.clicked.connect(self.set_piece_deleted)




        