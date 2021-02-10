import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from tkinter import *
from pandastable import Table, TableModel
from gen_rpt import gen_rpt
from chip import day_list

class TestApp(Frame):
        """Basic test frame for the table"""
        def __init__(self, parent=None):
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('600x400+200+100')
            self.main.title('Table app')
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            first_day = '20210101'
            last_day = '20210131'
            self.table = pt = Table(
                                    f, 
                                    dataframe=gen_rpt(day_list(first_day, last_day)).tip_rate(),
                                    showtoolbar=True, 
                                    showstatusbar=True,
                                    )
            pt.show()
            return

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Chip Data Processing'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        button = QPushButton('PyQt5 button', self)
        button.setToolTip('This is an example button')
        button.move(100,70)

    
if __name__ == '__main__':
    app = TestApp()
    app.mainloop()
