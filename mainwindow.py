from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QPushButton, QDialog, QListWidgetItem, QScrollBar, QListWidget, QMessageBox 
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import *

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import body

url = 'https://www.tradingview.com/chart/?symbol=NASDAQ%3AAMZN'

class InputWindow(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        uic.loadUi("select.ui",self)

        qwe = self.textEdit.toPlainText()
        # COMBOBOX 
        self.comboBox.addItem('1m')
        self.comboBox.addItem('5m')
        self.comboBox.addItem('15m')
        self.comboBox.addItem('30m')
        self.comboBox_2.addItem('A')
        self.comboBox_2.addItem('B')
        
    def closeEvent(self, event):
        if not self.authenticated:
            event.ignore()
    def keyPressEvent(self, event):
        if not event.key() == Qt.Key_Escape:
            super(InputWindow, self).keyPressEvent(event)
        

    def getResults(self):
        
        val1 = self.textEdit.toPlainText()
        val2 = self.comboBox.currentText()
        val3 = self.comboBox_2.currentText()
        return self.textEdit.toPlainText(), self.comboBox.currentText(), self.comboBox_2.currentText()
            


class MainWindow(QMainWindow):
    def __init__(self):
        # INIT
        super(MainWindow, self).__init__()
        uic.loadUi("untitled.ui",self)
        
        self.broker = body.client.broker()

        self.threaddict = {}

        # CONNECT INPUT
        self.pushButton.clicked.connect(self.getInputData)
        self.pushButton.setAutoDefault(False)
 
        self.listWidget_download.itemClicked.connect(self.Clicked) # connect itemClicked to Clicked method
        
        # BROWSER
        self.widget = QWebEngineView()
        self.widget.load(QUrl(url))
        self.gridLayout.addWidget(self.widget,1,0,1,3)

        # GRAPHICS
        self.pushButton_2.setIcon(QIcon('back.png'))
        
        ### 
        self.showMaximized()


    def Clicked(self, item):
        msg = QMessageBox()
        msg.setInformativeText('DELETE CONFIRMATION')
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Cancel)
        
        retval = msg.exec_()        

        if retval == QMessageBox.Ok:
            print('ok')
            self.removeSel(item)



    def removeSel(self,item):
        print(item.text())

        self.threaddict[str(item.text())].running = 0
        del self.threaddict[str(item.text())]


        print(self.threaddict)
        self.listWidget_download.takeItem(self.listWidget_download.row(item))
        # stop/delete download thread -> cancel order????



    def addToActiveDownloads(self, input1, input2, input3):
        
        item = QListWidgetItem(input1 + " / " + input2 + " / " + input3)

        fnt = (item.font())
        fnt.setBold(True)
        fnt.setPointSize(16)
        item.setFont(fnt)

        self.listWidget_download.addItem(item)
        self.threaddict[str(input1 + " / " + input2 + " / " + input3)] = body.download(input1,input2)
        self.threaddict[str(input1 + " / " + input2 + " / " + input3)].start()


    def getInputData(self):
        w = InputWindow(self)
        retval = w.exec_()
        if retval == QDialog.Accepted:
            val1,val2,val3 = w.getResults()
            self.addToActiveDownloads(val1,val2,val3)
        else:
            pass


    def back(self):
        self.widget.page().triggerAction(QWebEnginePage.Reload)

    def forward(self):
        self.widget.page().triggerAction(QWebEnginePage.Forward)

