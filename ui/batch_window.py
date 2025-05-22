# batch_window.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit

class BatchWindow(QDialog):
    def __init__(self, total_images, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Analysis")
        self.total_images = total_images
        self.analyzed_images = 0

        # Layout
        layout = QVBoxLayout()

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(total_images)
        layout.addWidget(self.progress_bar)

        # Results Display
        self.results_display = QTextEdit(self)
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)

        self.setLayout(layout)

    def update_progress(self, result):
        self.analyzed_images += 1
        self.progress_bar.setValue(self.analyzed_images)

        # Display the result
        self.results_display.append(
            f"Filename: {result['filename']}, "
            f"Total: {result['total_cells']}, "
            f"Green: {result['green_cells']}, "
            f"Red: {result['red_cells']}"
        )

