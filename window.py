import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon

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
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
