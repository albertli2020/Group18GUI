from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, QRect
from modules.file_loading import load_and_stitch_tiffs, get_grid_size
from modules.mouse_tracking import FileNameWidget, MouseTrackingLabel
from ui.tif_window import TifWindow
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tiff Viewer")
        self.setGeometry(100, 100, 1600, 1200)

        self.image_label = MouseTrackingLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.filename_widget = FileNameWidget(self)

        self.status_label = QLabel(self)

        load_button = QPushButton("Load Directory", self)
        load_button.clicked.connect(self.on_load_directory)

        layout = QVBoxLayout()
        layout.addWidget(self.filename_widget)
        layout.addWidget(self.image_label)
        layout.addWidget(load_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.grid_size = None
        self.directory = None

        self.image_label.mouse_position_changed.connect(self.filename_widget.update_filename)

        self.image_label.mousePressEvent = self.on_image_click


    def on_load_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory = directory
            self.grid_size = get_grid_size(directory)
            self.image_label.set_directory(directory)
            load_and_stitch_tiffs(directory, self.status_label, self.image_label)
            self.image_label.set_grid_size(self.grid_size)
            self.update()

    def on_image_click(self, event):
        if self.filename_widget.label.text():
            filename = self.filename_widget.label.text().replace("Current file: ", "")
            
            tiff_file_path = os.path.join(self.directory, filename)
            
            tif_window = TifWindow(self)
            tif_window.load_tiff_file(tiff_file_path, self.image_label.get_grid_size())
            tif_window.show()
