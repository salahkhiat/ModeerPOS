from .base_form import Form
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QFont 
from PyQt6.QtCore import pyqtSignal, QTimer

from .error_form import ErrorForm
from uis.error_msg import Ui_Dialog as ErrorFormUi

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ChooseItemForm(Form):
    item_barcode_sent = pyqtSignal(int)

    def __init__(self,base_form):
        super().__init__(base_form)
        
        self.setWindowTitle("إختر السلعة")
        # set icons
        self.set_icon("add_btn","add_item.svg")
        self.set_icon("cancel_btn","cancel.svg")
        # setup table 
        self.setup_table_columns()
        self.table : QTableWidget = self.ui.items_table
        self.remove_rows_counter(self.table)
        self.make_row_scrollable(self.table,1) 
        # initialize
        self.selected_item_barcode = None

        # database table details
        self.ui.name.textChanged.connect(lambda: self.put_data_into_table(self.get_product_name(),"name"))
        self.ui.ref.textChanged.connect(lambda: self.put_data_into_table(self.get_product_ref(),"barcode"))
        
        # connect buttons
        self.add_btn_clicked()
        

    def show_err_msg(self,msg:str):
        form = ErrorForm(ErrorFormUi)
        form.ui.err_msg.setText(msg.strip())
        QTimer.singleShot(2000,form.close)
        form.exec()

    def setup_table_columns(self):
        table: QTableWidget = self.ui.items_table
        
        header = table.horizontalHeader()
        
        # Column 0: stretch (name)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Column 1: fixed width
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        table.setColumnWidth(1, 120)

        # Column 2: fixed width
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        table.setColumnWidth(2, 120)


    def get_product_name(self):
        name = self.ui.name.text().strip()
        return name
    
    def get_product_ref(self):
        ref = self.ui.ref.text().strip()
        return ref
    
    def get_product_info(self, prefix:str, column:str):
        table = "products"
        targets = ["name", "barcode", "sale_price"]
        products = self.search_by_similar(table, column, prefix, targets, hide_0_quantity_item=True)
        return products

    def add_row(self, columns:list):
        table : QTableWidget = self.ui.items_table
        row_position = table.rowCount()
        table.insertRow(row_position)
        name, barcode, sale_price = columns

        # Set the size of table Font
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        
        # Create and set items with the font
        for col, value in enumerate([name, barcode, sale_price]):        
            table.setItem(row_position, col, self.make_item(value, font_size=14, read_only=True))
        print("this")

    def put_data_into_table(self, prefix:str, column:str):
        self.ui.items_table.setRowCount(0)

        products = self.get_product_info(prefix,column)
        for product in products :
            info = [product["name"], product["barcode"], product["sale_price"]]
            self.add_row(info)
    
    def get_item_quantity(self):
        table = "products"
        target = "quantity"
        column = "barcode"
        keyword = self.selected_item_barcode
        return self.search_by(table,column,keyword,target)

    def add_selected_item(self):    
        quantity = self.get_item_quantity()
        if quantity < 1:
            self.show_err_msg("الكمية نفذت")
            self.play_failure_sound()
        else:
            self.item_barcode_sent.emit(self.selected_item_barcode)
            self.close()
            self.play_success_sound()
        
    def add_btn_clicked(self):
        self.ui.add_btn.clicked.connect(self.add_selected_item)

    def make_row_scrollable(self, table: QTableWidget, column_index: int):
        # 1. Make table rows selectable (full row)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # 3. Connect to selection change signal
        def on_row_selected():
            selected_items = table.selectedItems()
            if selected_items:
                row = table.currentRow()
                item: QTableWidgetItem = table.item(row, column_index)
                if item:
                    self.selected_item_barcode = int(item.text())        

        # ✅ connect signal to update barcode whenever selection changes
        table.itemSelectionChanged.connect(on_row_selected)


    

    
    
    

        
        


