from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen

class MouseTrackingLabel(QLabel):
    mouse_position_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.grid_size = None
        self.file_pattern = "Pos{:d}_{:d}.ome.tif"

    def set_grid_size(self, grid_size):
        self.grid_size = grid_size

    def mouseMoveEvent(self, event):
        if self.pixmap() and self.grid_size:
            pos = event.position()
            pixmap_rect = self.get_pixmap_rect()
            
            if pixmap_rect.contains(pos.toPoint()):
                x = int(pos.x() - pixmap_rect.x())
                y = int(pos.y() - pixmap_rect.y())
                
                width = self.pixmap().width()
                height = self.pixmap().height()
                rows, cols = self.grid_size

                cell_width = width / cols
                cell_height = height / rows

                col = int(x // cell_width)
                row = int(y // cell_height)

                if 0 <= col < cols and 0 <= row < rows:
                    filename = self.file_pattern.format(col, rows - row - 1)
                    self.mouse_position_changed.emit(filename)
            else:
                self.mouse_position_changed.emit("")

        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap() and self.grid_size:
            painter = QPainter(self)
            pen = QPen(Qt.GlobalColor.lightGray, 1, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            
            pixmap_rect = self.get_pixmap_rect()
            painter.setClipRect(pixmap_rect)
            
            rows, cols = self.grid_size
            width = self.pixmap().width()
            height = self.pixmap().height()

            cell_width = width / cols
            cell_height = height / rows

            for i in range(1, rows):
                y = pixmap_rect.y() + i * cell_height * pixmap_rect.height() / height
                painter.drawLine(pixmap_rect.left(), int(y), pixmap_rect.right(), int(y))

            for i in range(1, cols):
                x = pixmap_rect.x() + i * cell_width * pixmap_rect.width() / width
                painter.drawLine(int(x), pixmap_rect.top(), int(x), pixmap_rect.bottom())

    def get_pixmap_rect(self):
        if self.pixmap():
            pixmap_size = self.pixmap().size()
            pixmap_size.scale(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            x = (self.width() - pixmap_size.width()) // 2
            y = (self.height() - pixmap_size.height()) // 2
            return QRect(x, y, pixmap_size.width(), pixmap_size.height())
        return QRect()

class FileNameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedHeight(60)

    def update_filename(self, filename):
        self.label.setText(f"Current file: {filename}" if filename else "")
