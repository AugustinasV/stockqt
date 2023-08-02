import mainwindow
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
   
    app = QApplication(sys.argv)
    window = mainwindow.MainWindow()
    
    sys.exit(app.exec())
