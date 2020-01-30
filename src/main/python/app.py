'''
GUI for converting an image to black-and-white
by adjusting its threshold using Wand API for ImageMagick.
'''

from os import path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget
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
        self.min_threshold_value = 25
        self.max_threshold_value = 75
        self.threshold_value_jump_interval = 5

        self.curr_idx = 0
        self.default_output_path = ''
        self.filenames = []
        self.input_images = []
        self.threshold_values = []

        self.init_ui()

        self.create_actions()
        self.create_menus()

    def reset_attributes(self):
        '''Reset class attributes to their default values'''
        self.curr_idx = 0
        self.default_output_path = ''
        self.filenames = []
        self.input_images = []
        self.threshold_values = []

    def init_ui(self):
        '''Initiates user interface.'''
        # === controls_layout ===
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(self.open_images)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(self.min_threshold_value)
        self.threshold_slider.setMaximum(self.max_threshold_value)
        self.threshold_slider.setSingleStep(1)
        self.threshold_slider.setValue(self.default_threshold_value)
        self.threshold_slider.setTickPosition(QSlider.TicksAbove)
        self.threshold_slider.setTickInterval(
            self.threshold_value_jump_interval)
        self.threshold_slider.setEnabled(False)
        self.threshold_slider.valueChanged.connect(
            self.on_threshold_val_change
        )

        self.save_btn = QPushButton('Save')
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_images)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(open_btn)
        controls_layout.addWidget(self.threshold_slider)
        controls_layout.addWidget(self.save_btn)

        # === display_layout ===
        self.prev_btn = QPushButton('<<')
        self.prev_btn.setEnabled(False)
        self.prev_btn.setFixedWidth(50)
        self.prev_btn.clicked.connect(self.prev_image)

        self.threshold_display = QLabel()
        self.threshold_display.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.threshold_display.setMaximumHeight(15)

        self.next_btn = QPushButton('>>')
        self.next_btn.setEnabled(False)
        self.next_btn.setFixedWidth(50)
        self.next_btn.clicked.connect(self.next_image)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.threshold_display)
        nav_layout.addWidget(self.next_btn)

        # === previews_layout ===
        alignment = Qt.AlignHCenter | Qt.AlignVCenter
        size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.input_preview_display = QLabel('Click "Open" to load image.')
        self.input_preview_display.setAlignment(alignment)
        self.input_preview_display.setSizePolicy(size_policy)

        self.output_preview_display = QLabel('Output preview will be here.')
        self.output_preview_display.setAlignment(alignment)
        self.output_preview_display.setSizePolicy(size_policy)

        previews_layout = QHBoxLayout()
        previews_layout.addWidget(self.input_preview_display)
        previews_layout.addWidget(self.output_preview_display)

        # === footer_layout ===

        footer = QLabel('Copyright (c) 2020 Prasanna Venkatesh T S')
        footer.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        footer.setMaximumHeight(15)

        footer_layout = QHBoxLayout()
        footer_layout.addWidget(footer)

        # === layout_wrapper ===
        layout_wrapper = QVBoxLayout()
        layout_wrapper.addLayout(controls_layout)
        layout_wrapper.addLayout(nav_layout)
        layout_wrapper.addLayout(previews_layout)
        layout_wrapper.addLayout(footer_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout_wrapper)

        self.setCentralWidget(central_widget)

        self.update_threshold_display()

    def create_actions(self):
        '''Creates actions.'''
        # === file actions ===
        self.action_open = QAction(
            '&Open...',
            self,
            shortcut='Ctrl+O',
            triggered=self.open_images
        )
        self.action_save = QAction(
            '&Save...',
            self,
            shortcut='Ctrl+S',
            triggered=self.save_images,
            enabled=False
        )

        # === edit actions ===
        self.action_incr_threshold = QAction(
            '&Increase Threshold',
            self,
            shortcut='Right',
            triggered=self.change_threshold_val(1),
            enabled=False
        )

        self.action_decr_threshold = QAction(
            '&Decrease Threshold',
            self,
            shortcut='Left',
            triggered=self.change_threshold_val(-1),
            enabled=False
        )
        self.action_incr_threshold_by_5 = QAction(
            'I&ncrease Threshold by 5%',
            self,
            shortcut='Shift+Right',
            triggered=self.change_threshold_val(5),
            enabled=False
        )
        self.action_decr_threshold_by_5 = QAction(
            'D&ecrease Threshold by 5%',
            self,
            shortcut='Shift+Left',
            triggered=self.change_threshold_val(-5),
            enabled=False
        )

        # === about actions ===
        self.action_show_about = QAction(
            '&About',
            self,
            triggered=self.show_about
        )
        self.action_show_about_qt = QAction(
            'About &Qt',
            self,
            triggered=lambda: QMessageBox.aboutQt(self)
        )

    def create_menus(self):
        '''Creates Menu Items in Menubar.'''
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)

        self.edit_menu = QMenu('&Edit', self)
        self.edit_menu.addAction(self.action_incr_threshold)
        self.edit_menu.addAction(self.action_decr_threshold)
        self.edit_menu.addAction(self.action_incr_threshold_by_5)
        self.edit_menu.addAction(self.action_decr_threshold_by_5)

        self.about_menu = QMenu('&Help', self)
        self.about_menu.addAction(self.action_show_about)
        self.about_menu.addAction(self.action_show_about_qt)

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.edit_menu)
        self.menuBar().addMenu(self.about_menu)

    def open_images(self):
        '''Handles `open_btn` click event.'''
        filepaths, _ = QFileDialog.getOpenFileNames(
            self,
            caption='Open file',
            filter='Image files (*.jpg *.jpeg *.png *.tiff *.tif *.gif)'
        )

        if filepaths:
            self.reset_attributes()
            self.load_images(filepaths)
            self.enable_ui()
            self.default_output_path = path.dirname(filepaths[0])

    def save_images(self):
        '''Handles `self.save_btn` click event.'''
        dirpath = QFileDialog.getExistingDirectory(
            self, 'Save to Folder', self.default_output_path)

        if dirpath:
            self.generate_output(dirpath)

    def on_threshold_val_change(self, value):
        '''Handles `self.threshold_slider` value change event.'''
        self.threshold_values[self.curr_idx] = value
        self.update_threshold_display()
        self.update_output_preview()

    def prev_image(self):
        '''Handles `self.prev_btn` click event.'''
        if self.curr_idx > 0:
            self.curr_idx -= 1
            self.update_ui()

    def next_image(self):
        '''Handles `self.next_btn` click event.'''
        if self.curr_idx < len(self.input_images) - 1:
            self.curr_idx += 1
            self.update_ui()

    def resizeEvent(self, event):  # pylint: disable=invalid-name
        '''
        Resizes the previews when window resizes.
        '''

        if self.input_images:
            self.update_previews()

        QMainWindow.resizeEvent(self, event)

    def change_threshold_val(self, change_by_value):
        '''Changes the current threshold value by the given value'''
        def _():
            curr_threshold_value = self.threshold_values[self.curr_idx]
            changed_threshold_val = curr_threshold_value + change_by_value

            if changed_threshold_val > self.max_threshold_value:
                changed_threshold_val = self.max_threshold_value
            elif changed_threshold_val < self.min_threshold_value:
                changed_threshold_val = self.min_threshold_value

            self.threshold_values[self.curr_idx] = changed_threshold_val
            self.update_ui()

        return _

    def show_about(self):
        '''Shows information about the app.'''
        msgbox = QMessageBox(self)
        msgbox.setWindowTitle(self.title)
        msgbox.setText(f'About {self.title}')
        msgbox.setInformativeText(
            'vMono is a GUI app to convert images (esp. scanned ones) to black-and-white'
            ' by controlling the image threshold.'
            '\n\n Uses ImageMagick through Wand API and Qt as GUI through PyQt5.'
        )
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec()

    def load_images(self, filepaths):
        '''
        Loads the image for the given `filepaths`
        and stores them in `self.input_images`.

        Set intial threshold value, for each image in `self.input_images`,
        in `self.threshold_values`.
        '''
        for filepath in filepaths:
            filename = path.basename(filepath)
            self.filenames.append(filename)

            input_image = Image(filename=filepath)
            self.input_images.append(input_image)

        self.threshold_values = [
            self.default_threshold_value
        ] * len(self.input_images)

        self.update_previews()

    def enable_ui(self):
        '''Enables the UI after an image is loaded.'''
        self.threshold_slider.setEnabled(True)
        self.update_window_title()

        self.save_btn.setEnabled(True)
        self.prev_btn.setEnabled(True)
        self.next_btn.setEnabled(True)
        self.action_save.setEnabled(True)
        self.action_incr_threshold.setEnabled(True)
        self.action_decr_threshold.setEnabled(True)
        self.action_incr_threshold_by_5.setEnabled(True)
        self.action_decr_threshold_by_5.setEnabled(True)

    def update_ui(self):
        '''Updates UI whenever `self.curr_idx` changes.'''
        self.update_previews()
        self.update_threshold_display()
        self.update_window_title()
        self.repaint()

    def update_window_title(self):
        '''Adds the current preview's filename to the window's title.'''
        self.setWindowTitle(f'{self.title} | {self.filenames[self.curr_idx]}')

    def update_threshold_display(self):
        '''
        Updates `self.threshold_display` and `self.threshold_slider`
        with a value in `self.threshold_values` according to the `self.curr_idx`.
        '''
        curr_threshold_value = (
            self.threshold_values[self.curr_idx]
            if self.threshold_values
            else self.default_threshold_value
        )
        self.threshold_slider.setValue(curr_threshold_value)
        self.threshold_display.setText(f'{curr_threshold_value}%')

    def update_previews(self):
        '''Update the input and output previews.'''

        self.update_input_preview()
        self.update_output_preview()

    def update_input_preview(self):
        '''
        Updates `self.input_preview_display` with the copy of a image
        from `self.input_images` according to the `self.curr_idx`.
        '''
        input_preview_img = self.input_images[self.curr_idx].clone()
        input_preview_pixmap = generate_preview(
            input_preview_img,
            self.input_preview_display.size()
        )
        self.input_preview_display.setPixmap(input_preview_pixmap)

    def update_output_preview(self):
        '''
        Updates `self.output_preview_display` with the copy of a image
        from `self.input_images` set to the threshold value
        according to the `self.curr_idx`.
        '''
        output_preview_img = self.input_images[self.curr_idx].clone()
        output_preview_img.threshold(
            self.threshold_values[self.curr_idx] / 100
        )
        output_preview_pixmap = generate_preview(
            output_preview_img,
            self.output_preview_display.size()
        )
        self.output_preview_display.setPixmap(output_preview_pixmap)

    def generate_output(self, dirpath):
        '''
        For each opened file, make output filepath and write output
        if the output filepath does not already exists
        or the user agrees to replace the existing file.
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

        self.show_saved_msg(dirpath)

    def confirm_replace(self, filename, dirname):
        '''
        Show a warning messagebox to confirm
        if the user agrees to replace the existing file
        and return user response.
        '''
        msgbox = QMessageBox(self)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setWindowTitle(self.title)
        msgbox.setText(
            f'“{filename}" already exists. Do you want to replace it?'
        )
        msgbox.setInformativeText(
            f'A file with the same name already exists in the folder "{dirname}". '
            'Replacing it will overwrite it.'
            '\n\n Tip: If you do not want to replace it, click "Cancel" and '
            'select a different folder.'
        )
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        response = msgbox.exec()

        return response == QMessageBox.Ok

    def write_output(self, filepath, idx):
        '''
        Makes output images for the images in `self.input_images`
        with the corresponding threshold values in `self.threshold_values`
        and saves it to the given filepath.
        '''
        img = self.input_images[idx].clone()
        img.threshold(self.threshold_values[idx] / 100)
        img.save(filename=filepath)

    def show_saved_msg(self, output_dirpath):
        '''
        Shows the message saying that the images files have been saved
        to the selected output folder.
        '''
        msgbox = QMessageBox(self)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setWindowTitle(self.title)
        msgbox.setText('Saved output images to the selected folder.')
        msgbox.setInformativeText(
            (f'Saved image files to "{output_dirpath}"')
        )
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec()
