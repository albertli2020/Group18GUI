from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from modules.file_loading import load_and_stitch_tiffs

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TIFF Analysis Application")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout (Vertical)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Status Label (for displaying "Stitching")
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # Image Display Area (Placeholder)
        self.image_label = QLabel("Stitched Image Display Area")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.main_layout.addWidget(self.image_label)

        # Button Layout (Horizontal)
        self.button_layout = QHBoxLayout()
        
        # Load Directory Button
        self.load_directory_button = QPushButton("Load Directory")
        self.load_directory_button.clicked.connect(self.on_load_directory)
        self.button_layout.addWidget(self.load_directory_button)

        # Add Button Layout to Main Layout
        self.main_layout.addLayout(self.button_layout)

    def on_load_directory(self):
        # Open file dialog to select the directory containing TIFF files
        directory = QFileDialog.getExistingDirectory(self, "Select TIFF Directory")
        print(directory)
        if directory:
            load_and_stitch_tiffs(directory, self.status_label, self.image_label)

