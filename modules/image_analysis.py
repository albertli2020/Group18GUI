import numpy as np
import tifffile as tif
from cellpose import models
from skimage import filters, measure, morphology

def analyze_image(filepath, img_index):
    # Load the image
    tif_stack = tif.imread(filepath)
    blue_channel = tif_stack[img_index][0]
    green_channel = tif_stack[img_index][1]
    red_channel = tif_stack[img_index][2]

    # Segment cells using Cellpose
    model = models.Cellpose(gpu=True, model_type='cyto')
    masks, _, _, _ = model.eval(blue_channel, diameter=None, channels=[0,0])

    # Process green channel
    green_threshold = np.percentile(green_channel, 99)  # Use 99th percentile
    green_binary = green_channel > green_threshold
    green_binary = morphology.remove_small_objects(green_binary, min_size=20)
    green_binary = morphology.binary_closing(green_binary, morphology.disk(3))
    
    # Process red channel
    red_threshold = filters.threshold_otsu(red_channel)
    red_binary = red_channel > red_threshold

    # Overlay masks on green and red channels
    green_overlay = np.zeros_like(masks, dtype=bool)
    red_overlay = np.zeros_like(masks, dtype=bool)

    for cell in measure.regionprops(masks):
        cell_mask = masks == cell.label
        if np.sum(cell_mask & green_binary) / np.sum(cell_mask) > 0.2:  # At least 20% overlap
            green_overlay |= cell_mask
        if np.sum(cell_mask & red_binary):
            red_overlay |= cell_mask

    # Count cells
    total_cells = np.max(masks)
    green_cells = np.max(measure.label(green_overlay))
    red_cells = np.max(measure.label(red_overlay))

    return {
        'masks': masks,
        'green_overlay': green_overlay,
        'red_overlay': red_overlay,
        'total_cells': total_cells,
        'green_cells': green_cells,
        'red_cells': red_cells
    }