from PyQt6.QtCore import QObject, pyqtSignal, QEvent, Qt


class BarcodeScanner(QObject):

    barcodeScanned = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.buffer = ""

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Type.KeyPress:

            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):

                barcode = self.buffer
                self.buffer = ""

                if barcode:
                    self.barcodeScanned.emit(barcode)

            else:
                text = event.text()
               

                if text:
                    self.buffer += text

        return False