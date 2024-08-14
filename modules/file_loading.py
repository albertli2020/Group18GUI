import os
import re
import tifffile as tif
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
import scipy.ndimage
from skimage import exposure

def postoindex(x, y, max_x, max_y):
    if y % 2 == 0:
        return y * (max_y + 1) + x
    else:
        return (y // 2 + 1) * (max_x + max_y + 2) - x - 1

file_pattern = r"Pos(\d+)_(\d+)"
def file_generator(base_dir):
    files = []
    for filename in sorted(os.listdir(base_dir)):
        if filename.endswith('.ome.tif'):
            match = re.search(file_pattern, filename)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                files.append((filename, x, y))
    
    print("Files to be processed:")
    for f in files:
        print(f)
    
    for file in files:
        yield file

def apply_clahe_rgb(image, clip_limit=0.03):
    return np.stack([exposure.equalize_adapthist(image[:,:,i], clip_limit=clip_limit) for i in range(3)], axis=-1)


def load_and_stitch_tiffs(directory, status_label, image_label):
    status_label.setText("Stitching...")
    status_label.repaint()

    max_x, max_y = 0, 0
    for filename, x, y in file_generator(directory):
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    print(max_x, max_y)

    tif_path = os.path.join(directory, sorted(os.listdir(directory))[4])
    print(tif_path)
    tif_stack = tif.imread(tif_path) 
    image_shape = tif_stack.shape
    print(image_shape)
    num_images, num_channels, image_height, image_width = tif_stack.shape

    stack_bgr_images = tif_stack.transpose(0, 2, 3, 1)  # Shape: (400, 1200, 1200, 3)
    print(f'Shape after transposition: {stack_bgr_images.shape}')

    stitched_image = np.zeros(((max_y + 1) * image_height, (max_x + 1) * image_width, num_channels), dtype=stack_bgr_images.dtype)   

    total_tiles = (max_x + 1) * (max_y + 1)
    processed_tiles = 0 

    for filename, x, y in file_generator(directory):
        index = postoindex(x, y, max_x, max_y)
        stitched_y = max_y - y
        stitched_x = x
        print(f"Placing {filename} at (x={stitched_x}, y={stitched_y}), index={index}")
        if (stitched_y + 1) * image_height <= stitched_image.shape[0] and (stitched_x + 1) * image_width <= stitched_image.shape[1]:
            stitched_image[
                stitched_y * image_height:(stitched_y + 1) * image_height,
                stitched_x * image_width:(stitched_x + 1) * image_width
            ] = stack_bgr_images[index]
        else:
            print(f"Warning: Tile at ({x}, {y}) exceeds stitched image boundaries")


        processed_tiles += 1

    print(f"Processed {processed_tiles} out of {total_tiles} expected tiles")

    resized_image = scipy.ndimage.zoom(stitched_image, (0.25, 0.25, 1), order=1)
    print("finished resizing")
    red_max = np.max(resized_image[:,:,0])
    print("red done")
    green_max = np.max(resized_image[:,:,1])
    print("green done")
    blue_max = np.max(resized_image[:,:,2])
    print("blue done")
    stacked_image = np.stack((resized_image[:,:,0] / red_max, resized_image[:,:,1] / green_max, resized_image[:,:,2] / blue_max), axis=-1)
    print("done")
    stacked_image = apply_clahe_rgb(stacked_image)
    
    plt.imshow(stacked_image)
    plt.title("Stitched Image")
    plt.axis('off')
    plt.imsave("stitched_image.png", stacked_image)

    # Display the stitched image in the QLabel
    print("Reading...")
    image = QImage("stitched_image.png")
    print("Setting up Pixmap")
    pixmap = QPixmap.fromImage(image)
    image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    # Clear the status label
    status_label.setText("")

def get_grid_size(directory):
    max_x, max_y = 0, 0
    for _, x, y in file_generator(directory):
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    return (max_y + 1, max_x + 1)
