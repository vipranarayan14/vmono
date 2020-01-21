'''
GUI for converting an image to black-and-white
by adjusting its threshold using Wand API for ImageMagick.
'''

from os import path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSlider
)

from wand.image import Image


def generate_preview(image, size):
    '''Generates preview for the given `image` as a QPixmap.'''
    image.compression_quality = 50
    image_binary = image.make_blob()
    q_image = QImage.fromData(image_binary)
    q_pixmap = QPixmap.fromImage(q_image)
    q_pixmap_scaled = q_pixmap.scaled(size, Qt.KeepAspectRatio)
    return q_pixmap_scaled


class MainWindow(QMainWindow):
    '''Subclass extending QMainWindow for customization.'''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('vMono')
        self.resize(1000, 800)

        self.image = None
        self.threshold_val = 55

        self.init_ui()

    def init_ui(self):
        '''Initiates user interface.'''
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
        self.threshold_slider.valueChanged.connect(
            self.on_threshold_val_change
        )

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
        self.threshold_display.setMaximumHeight(15)

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

    def on_open_btn_click(self):
        '''Handles `open_btn` click event.'''
        filepath, _ = QFileDialog.getOpenFileName(
            self, caption='Open file', filter='Image files (*.jpg)'
        )

        if filepath:
            self.load_img(filepath)
            self.enable_ui()

    def on_save_btn_click(self):
        '''Handles `self.save_btn` click event.'''
        filepath, _ = QFileDialog.getSaveFileName(self, caption='Save File')

        if filepath:
            self.generate_output(filepath)

    def on_threshold_val_change(self, value):
        '''Handles `self.threshold_slider` value change event.'''
        self.threshold_val = value
        self.update_threshold_display()
        self.update_output_preview()

    def update_threshold_display(self):
        '''Updates `self.threshold_display` with current value in `self.threshold_val`.'''
        self.threshold_display.setText(str(self.threshold_val) + '%')

    def load_img(self, filepath):
        '''Loads the image from the given `filepath`.'''
        self.image = Image(filename=filepath)
        self.setWindowTitle(self.windowTitle() + ' |  ' + filepath)
        self.show_previews()

    def enable_ui(self):
        '''Enables the UI after an image is loaded.'''
        self.threshold_slider.setEnabled(True)
        self.save_btn.setEnabled(True)

    def show_previews(self):
        '''Shows input and output previews.'''
        self.show_input_preview()
        self.update_output_preview()

    def show_input_preview(self):
        '''Shows the preview of the input image in `self.image`.'''
        input_preview_img = self.image.clone()
        input_preview_pixmap = generate_preview(
            input_preview_img,
            self.input_preview.size()
        )
        self.input_preview.setPixmap(input_preview_pixmap)

    def update_output_preview(self):
        '''
        Updates `self.output_preview` with a new copy of the `self.image`
        set to current value in `self.threshold_val`.
        '''
        output_preview_img = self.image.clone()
        output_preview_img.threshold(self.threshold_val / 100)
        output_preview_pixmap = generate_preview(
            output_preview_img,
            self.output_preview.size()
        )
        self.output_preview.setPixmap(output_preview_pixmap)

    def generate_output(self, filepath):
        '''
        Generates output with current value in `self.threshold_val`
        and saves it to the given filepath.
        '''
        img = self.image.clone()
        img.threshold(self.threshold_val / 100)
        img.save(filename=path.abspath(filepath))
