from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from modules.file_loading import load_and_stitch_tiffs, get_grid_size
from modules.mouse_tracking import FileNameWidget, MouseTrackingLabel
from modules.batch_analysis import run_batch_analysis
from ui.tif_window import TifWindow
from ui.batch_window import BatchWindow
import os
 
class AnalysisThread(QThread):
    update_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(list)

    def __init__(self, directory, grid_size):
        super().__init__()
        self.directory = directory
        self.grid_size = grid_size

    def run(self):
        results = run_batch_analysis(self.directory, self.grid_size, self.update_signal.emit)
        self.finished_signal.emit(results)

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

        #single_image_button = QPushButton("Load Single FOV", self)
        #single_image_button.clicked.connect(self.load_single_FOV)

        analysis_button = QPushButton("Complete Analysis", self)
        analysis_button.clicked.connect(self.on_complete_analysis)


        layout = QVBoxLayout()
        layout.addWidget(self.filename_widget)
        layout.addWidget(self.image_label)
        layout.addWidget(load_button)
        layout.addWidget(analysis_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.grid_size = None
        self.directory = None

        self.image_label.mouse_position_changed.connect(self.filename_widget.update_filename)

        self.image_label.mousePressEvent = self.on_image_click

    def load_single_FOV(self):
        directory = QFileDialog.getExistingDirectory(self, "Select FOV")
        if directory:
            self.directory = directory
            self.grid_size = get_grid_size(directory)
            self.image_label.set_directory(directory)


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

    def on_complete_analysis(self):
        if self.directory and self.grid_size:
            total_images = self.grid_size[0] * self.grid_size[1]
            self.batch_window = BatchWindow(total_images, self)
            self.batch_window.show()

            self.analysis_thread = AnalysisThread(self.directory, self.grid_size)
            self.analysis_thread.update_signal.connect(self.batch_window.update_progress)
            self.analysis_thread.finished_signal.connect(self.on_analysis_finished)
            self.analysis_thread.start()

    def on_analysis_finished(self, results):
        # Handle completion, e.g., show a message box
        print("Analysis completed")
