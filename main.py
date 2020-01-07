'''Python bindings for qt5.'''
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

from wand.image import Image

class MainWindow(QMainWindow):
    '''Subclass extending QMainWindow for customization.'''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('Learning Qt with PyQt')

        img = Image(filename='../vmono/samples/9.jpg')
        img.threshold(0.5)

        image_preview = QLabel()
        image_preview.setPixmap(QPixmap.fromImage(QImage.fromData(img.make_blob())))

        self.setCentralWidget(image_preview)

APP = QApplication([])

WINDOW = MainWindow()

WINDOW.show()

APP.exec()  # exec() = exec_() in PyQt5
