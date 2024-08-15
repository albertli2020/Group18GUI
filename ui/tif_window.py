from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from modules.image_display import display_image
from PyQt6.QtCore import Qt

class TifWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tiff Image")
        self.setGeometry(200, 200, 800, 800)
        
        self.status_label = QLabel(self)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.status_label)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def load_tiff_file(self, tiff_file_path, grid_size):
        display_image(tiff_file_path, self.layout, self.status_label, grid_size)
