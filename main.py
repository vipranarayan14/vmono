'''Python bindings for qt5.'''
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QSizePolicy, QSlider

from wand.image import Image

from os import path

class MainWindow(QMainWindow):
    '''Subclass extending QMainWindow for customization.'''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('vmono')
        self.resize(1000, 800)

        self.threshold_val = 55

        self.initUI()

    def initUI(self):
        # === controls_layout ===
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(self.on_open_btn_click)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(25)
        self.threshold_slider.setMaximum(75)
        self.threshold_slider.setSingleStep(1)
        self.threshold_slider.setTickPosition(QSlider.TicksAbove)
        self.threshold_slider.setTickInterval(5)
        self.threshold_slider.setValue(self.threshold_val)
        self.threshold_slider.setEnabled(False)
        self.threshold_slider.valueChanged.connect(self.on_threshold_val_change)

        self.save_btn = QPushButton('Save')
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.on_save_btn_click)


        controls_layout = QHBoxLayout()
        controls_layout.addWidget(open_btn)
        controls_layout.addWidget(self.threshold_slider)
        controls_layout.addWidget(self.save_btn)

        # === display_layout ===
        self.threshold_display = QLabel()
        self.threshold_display.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.threshold_display.setMaximumHeight(15)      # TODO: Make this relative to window size

        display_layout = QHBoxLayout()
        display_layout.addWidget(self.threshold_display)

        # === previews_layout ===
        self.input_preview = QLabel('Click "Open" to load image.')
        self.input_preview.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.output_preview = QLabel('Output preview will be here.')
        self.output_preview.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


        previews_layout = QHBoxLayout()
        previews_layout.addWidget(self.input_preview)
        previews_layout.addWidget(self.output_preview)

        # === layout_wrapper ===
        layout_wrapper = QVBoxLayout()
        layout_wrapper.addLayout(controls_layout)
        layout_wrapper.addLayout(display_layout)
        layout_wrapper.addLayout(previews_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout_wrapper)

        self.setCentralWidget(central_widget)

        self.update_threshold_display()

    def load_img(self, filename):
        self.image = Image(filename=filename)
        self.input_preview_img = self.image.clone()
        self.show_previews()

    def enableUI(self):
        self.threshold_slider.setEnabled(True)
        self.save_btn.setEnabled(True)

    def on_open_btn_click(self):
        filedesc = QFileDialog.getOpenFileName(
            self, 'Open file', '', 'Image files (*.jpg)')

        if filedesc:
            filename = filedesc[0]
            self.load_img(filename)
            self.enableUI()
        
        # TODO: on cancel

    @staticmethod
    def generate_preview(image, width, height):
        image.transform(resize='500x500>')
        print(width, height)
        pixmap = QPixmap.fromImage(QImage.fromData(image.make_blob()))
        pixmap.scaled(width, height, Qt.KeepAspectRatio)
        return pixmap

    def show_previews(self):
        self.input_preview.setPixmap(self.generate_preview(self.input_preview_img, self.input_preview.width(), self.input_preview.height()))
        self.update_output_preview()

    def update_threshold_display(self):
        self.threshold_display.setText(str(self.threshold_val) + '%')

    def update_output_preview(self):
        output_preview_img = self.image.clone()
        output_preview_img.threshold(self.threshold_val / 100)
        self.output_preview.setPixmap(self.generate_preview(output_preview_img, self.output_preview.width(), self.output_preview.height()))

    def on_threshold_val_change(self, value):
        self.threshold_val = value
        self.update_threshold_display()
        self.update_output_preview()

    def on_save_btn_click(self):
        filedesc = QFileDialog.getSaveFileName(self, 'Save File')
        if filedesc:
            filename = filedesc[0]
            img = self.image.clone()
            img.threshold(self.threshold_val / 100)
            img.save(filename=path.abspath(filename))

APP = QApplication([])

WINDOW = MainWindow()

WINDOW.show()

APP.exec()
