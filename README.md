ModeerGSM-V1.6 is a simple shop manager.
Develped by Salah Khiat

Folder build (faster startup):
py -m nuitka main.py --standalone --enable-plugin=pyqt6 --windows-disable-console --windows-icon-from-ico=modeer_logo.ico

Onefile build (single exe):
py -m nuitka main.py --standalone --onefile --enable-plugin=pyqt6 --windows-disable-console --windows-icon-from-ico=modeer_logo.ico
x