from skimage.measure import regionprops
import tifffile as tif
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import QThread, pyqtSignal
from modules.image_analysis import analyze_image
import os, re

file_pattern = r"Pos(\d+)_(\d+)"
def postoindex(x, y, max_x, max_y):
    if y % 2 == 0:
        return y * (max_y ) + x
    else:
        return (y // 2 + 1) * (max_x + max_y) - x - 1
    
class AnalysisThread(QThread):
    analysis_complete = pyqtSignal(dict)
    status_update = pyqtSignal(str)

    def __init__(self, filepath, img_index):
        super().__init__()
        self.filepath = filepath
        self.img_index = img_index

    def run(self):
        self.status_update.emit("Running Analysis")
        results = analyze_image(self.filepath, self.img_index)
        self.status_update.emit("Analysis Complete")
        self.analysis_complete.emit(results)


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(20, 10))  
        self.axs = self.fig.subplots(2, 4)  
        super().__init__(self.fig)
        self.setParent(parent)

def display_image(filepath, layout, status_label, grid_size):
    # Load the image
    img = tif.imread(filepath)
    match = re.search(file_pattern, filepath.split('/')[-1])
    max_x, max_y = grid_size
    img_index = None
    if match:
        x, y = int(match.group(1)), int(match.group(2))
        img_index = postoindex(x, y, max_x, max_y)

    # Separate the channels
    print(img.shape)
    blue_channel = img[img_index][0, :, :]
    green_channel = img[img_index][1, :, :]
    red_channel = img[img_index][2, :, :]
    
    canvas = MatplotlibCanvas()
    
    # Display each channel
    # Blue channel
    print("----------BLUE CHANNEL----------")
    cmap = mcolors.LinearSegmentedColormap.from_list('black_blue', [(0, 'black'), (1, 'blue')])
    blue_max = np.max(blue_channel)
    normalized_image = blue_channel / blue_max
    img = cmap(normalized_image)
    canvas.axs[1, 0].imshow(img)
    canvas.axs[1, 0].set_title('Blue Channel (DAPI)')
    canvas.axs[1, 0].axis('off')

    # Green channel
    print("----------GREEN CHANNEL----------")
    cmap = mcolors.LinearSegmentedColormap.from_list('black_green', [(0, 'black'), (1, 'green')])
    green_max = np.max(green_channel)
    normalized_image = green_channel/ green_max
    img = cmap(normalized_image)
    canvas.axs[0, 1].imshow(img)
    canvas.axs[0, 1].set_title('Green Channel (IBA1)')
    canvas.axs[0, 1].axis('off')

    # Red channel
    print("----------RED CHANNEL----------")
    cmap = mcolors.LinearSegmentedColormap.from_list('black_red', [(0, 'black'), (1, 'red')])
    red_max = np.max(red_channel)
    normalized_image = red_channel / red_max
    img = cmap(normalized_image)
    canvas.axs[0, 0].imshow(img)
    canvas.axs[0, 0].set_title('Red Channel (GFAP)')
    canvas.axs[0, 0].axis('off')

    # Display the merged image
    merged_image = np.stack((red_channel / red_max, green_channel / green_max, blue_channel / blue_max), axis=-1)
    #merged_image = np.stack((red_channel, green_channel, blue_channel), axis=-1)
    canvas.axs[1, 1].imshow(merged_image)
    canvas.axs[1, 1].set_title("Merged Channels")
    canvas.axs[1, 1].axis('off')

    for ax in canvas.axs[:, 2:].flatten():
        ax.remove()

    canvas.fig.tight_layout()
    canvas.draw()

    layout.addWidget(canvas)

    ax_big = canvas.fig.add_subplot(1, 2, 2)
    ax_big.axis('off')

    filename = os.path.basename(filepath)
    canvas.fig.suptitle(f"File: {filename}", fontsize=16)

    analysis_thread = AnalysisThread(filepath, img_index)
    analysis_thread.status_update.connect(status_label.setText)
    analysis_thread.analysis_complete.connect(lambda results: display_analysis_result(canvas, results))
    analysis_thread.start()


    canvas.fig.tight_layout()
    canvas.draw()
    layout.addWidget(canvas)

def display_analysis_result(canvas, results):
    ax = canvas.fig.add_subplot(1, 2, 2)
    
    # Create RGB image for overlay
    overlay = np.zeros((*results['masks'].shape, 3), dtype=float)
    overlay[results['green_overlay'], 1] = 1  # Green channel
    overlay[results['red_overlay'], 0] = 1    # Red channel
    
    # Overlay masks on original image
    original_red = canvas.axs[1, 0].images[0].get_array()
    original_green = canvas.axs[0, 1].images[0].get_array()
    original_blue = canvas.axs[0, 0].images[0].get_array()
    
    # Ensure we're only using the RGB channels
    if original_red.ndim == 3 and original_red.shape[2] == 4:
        original_red = original_red[..., :3]
    if original_green.ndim == 3 and original_green.shape[2] == 4:
        original_green = original_green[..., :3]
    if original_blue.ndim == 3 and original_blue.shape[2] == 4:
        original_blue = original_blue[..., :3]
    
    # Combine channels
    original = np.stack((
        original_red[..., 0],  # Red channel
        original_green[..., 1],  # Green channel
        original_blue[..., 2]  # Blue channel
    ), axis=-1)
    
    # Normalize the original image
    original = original / np.max(original)
    
    combined = original * 0.7 + overlay * 0.3  # Adjust these values to change the overlay intensity

    ax.imshow(combined)
    ax.set_title(f"Overlay (Total: {results['total_cells']}, "
                 f"Green: {results['green_cells']}, "
                 f"Red: {results['red_cells']})")
    ax.axis('off')

    canvas.fig.tight_layout()
    canvas.draw()

'''
def display_analysis_result(canvas, ax, labeled_mask, cell_count):
    im = ax.imshow(labeled_mask, cmap='nipy_spectral')
    ax.set_title(f"Labeled Mask (Total cells: {cell_count})")
    ax.axis('off')

    for region in regionprops(labeled_mask):
        if region.area < 50:
            continue
        y, x = region.centroid
        ax.text(x, y, str(region.label), fontsize=8, color='white', 
                ha='center', va='center')

    canvas.fig.tight_layout()
    canvas.fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    canvas.draw()
'''