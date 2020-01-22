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
    QSlider,
    QMessageBox
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

        self.title = 'vMono'

        self.setWindowTitle(self.title)
        self.resize(1000, 800)

        self.default_threshold_value = 55

        self.curr_idx = 0
        self.filenames = []
        self.default_output_path = ''

        self.input_images = []
        self.input_previews = []
        self.output_previews = []
        self.threshold_values = []

        self.init_ui()

    def init_attributes(self):
        self.curr_idx = 0
        self.filenames = []
        self.default_output_path = ''

        self.input_images = []
        self.input_previews = []
        self.output_previews = []
        self.threshold_values = []

    def init_ui(self):
        '''Initiates user interface.'''
        # === controls_layout ===
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(self.on_open_btn_click)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(25)
        self.threshold_slider.setMaximum(75)
        self.threshold_slider.setSingleStep(1)
        self.threshold_slider.setValue(self.default_threshold_value)
        self.threshold_slider.setTickPosition(QSlider.TicksAbove)
        self.threshold_slider.setTickInterval(5)
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
        self.prev_btn = QPushButton('<<')
        self.prev_btn.setEnabled(False)
        self.prev_btn.setFixedWidth(50)
        self.prev_btn.clicked.connect(self.on_prev_btn_click)

        self.threshold_display = QLabel()
        self.threshold_display.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.threshold_display.setMaximumHeight(15)

        self.next_btn = QPushButton('>>')
        self.next_btn.setEnabled(False)
        self.next_btn.setFixedWidth(50)
        self.next_btn.clicked.connect(self.on_next_btn_click)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.threshold_display)
        nav_layout.addWidget(self.next_btn)

        # === previews_layout ===

        self.input_preview_display = QLabel('Click "Open" to load image.')
        self.input_preview_display.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.output_preview_display = QLabel('Output preview will be here.')
        self.output_preview_display.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        previews_layout = QHBoxLayout()
        previews_layout.addWidget(self.input_preview_display)
        previews_layout.addWidget(self.output_preview_display)

        # === layout_wrapper ===
        layout_wrapper = QVBoxLayout()
        layout_wrapper.addLayout(controls_layout)
        layout_wrapper.addLayout(nav_layout)
        layout_wrapper.addLayout(previews_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout_wrapper)

        self.setCentralWidget(central_widget)

        self.update_threshold_display()

    def on_open_btn_click(self):
        '''Handles `open_btn` click event.'''
        filepaths, _ = QFileDialog.getOpenFileNames(
            self, caption='Open file', filter='Image files (*.jpg *.jpeg *.png *.tiff *.tif *.gif)'
        )

        if filepaths:
            self.init_attributes()
            self.load_img(filepaths)
            self.enable_ui()
            self.default_output_path = path.dirname(filepaths[0])

    def on_save_btn_click(self):
        '''Handles `self.save_btn` click event.'''
        dirpath = QFileDialog.getExistingDirectory(self, 'Save to Folder', self.default_output_path)

        if dirpath:
            self.generate_output(dirpath)

    def on_threshold_val_change(self, value):
        '''Handles `self.threshold_slider` value change event.'''
        self.threshold_values[self.curr_idx] = value
        self.update_threshold_display()
        self.update_output_preview()

    def on_prev_btn_click(self):
        if self.curr_idx > 0:
            self.curr_idx -= 1
            self.update_ui()

    def on_next_btn_click(self):
        if self.curr_idx < len(self.input_images) - 1:
            self.curr_idx += 1
            self.update_ui()

    def update_ui(self):
        self.display_previews()
        self.update_threshold_display()
        self.update_window_title()

    def update_window_title(self):
        self.setWindowTitle(self.title + ' |  ' + self.filenames[self.curr_idx])

    def update_threshold_display(self):
        '''Updates `self.threshold_display` with current value in `self.default_threshold_value`.'''
        curr_threshold_value = (
            self.threshold_values[self.curr_idx]
            if self.threshold_values
            else self.default_threshold_value
        )
        self.threshold_slider.setValue(curr_threshold_value)
        self.threshold_display.setText(str(curr_threshold_value) + '%')

    def load_img(self, filepaths):
        '''Loads the image from the given `filepath`.'''
        for filepath in filepaths:
            filename = path.basename(filepath)
            self.filenames.append(filename)

            input_image = Image(filename=filepath)
            self.input_images.append(input_image)

        self.generate_previews()
        self.display_previews()

    def generate_input_previews(self, img):
        input_preview_img = img.clone()
        input_preview_pixmap = generate_preview(
            input_preview_img,
            self.input_preview_display.size()
        )
        self.input_previews.append(input_preview_pixmap)

    def generate_previews(self):
        self.threshold_values = [self.default_threshold_value] * len(self.input_images)

        for img in self.input_images:
            self.generate_input_previews(img)

    def enable_ui(self):
        '''Enables the UI after an image is loaded.'''
        self.threshold_slider.setEnabled(True)
        self.update_window_title()

        self.save_btn.setEnabled(True)
        self.prev_btn.setEnabled(True)
        self.next_btn.setEnabled(True)

    def display_previews(self):
        '''Shows the preview of the input image in `self.image`.'''

        self.input_preview_display.setPixmap(self.input_previews[self.curr_idx])
        self.update_output_preview()

    def update_output_preview(self):
        '''
        Updates `self.output_preview_display` with a new copy of the `self.image`
        set to current value in `self.default_threshold_value`.
        '''
        output_preview_img = self.input_images[self.curr_idx].clone()
        output_preview_img.threshold(self.threshold_values[self.curr_idx] / 100)
        output_preview_pixmap = generate_preview(
            output_preview_img,
            self.output_preview_display.size()
        )
        self.output_preview_display.setPixmap(output_preview_pixmap)

    def generate_output(self, dirpath):
        '''
        Generates output with current value in `self.default_threshold_value`
        and saves it to the given filepath.
        '''
        for idx, filename in enumerate(self.filenames):

            output_filepath = path.join(path.abspath(dirpath), filename)

            if path.exists(output_filepath):
                dirname = path.split(dirpath)[1]
                affrimative = self.confirm_replace(filename, dirname)

                if affrimative:
                    self.write_output(output_filepath, idx)

            else:
                self.write_output(output_filepath, idx)

    def confirm_replace(self, filename, dirname):
        msgbox = QMessageBox(self)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setWindowTitle(self.title)
        msgbox.setText(f'“{filename}" already exists. Do you want to replace it?')
        msgbox.setInformativeText(
            (f'A file with the same name already exists in the folder "{dirname}". '
             'Replacing it will overwrite it.'
             '\n\n Tip: If you do not want to replace it, click "Cancel" and '
             'select a different folder.')
        )
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        response = msgbox.exec()

        return response == QMessageBox.Ok

    def write_output(self, filepath, idx):
        img = self.input_images[idx].clone()
        img.threshold(self.threshold_values[idx] / 100)
        img.save(filename=filepath)
