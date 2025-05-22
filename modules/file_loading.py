import os
import re
import tifffile as tif
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
import scipy.ndimage
from skimage import exposure
import cv2

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
    image = np.clip(image, 0, 1).astype(np.float32)
    print(f"CLAHE input min: {image.min()}, max: {image.max()}")  
    result = np.stack([exposure.equalize_adapthist(image[:,:,i], clip_limit=clip_limit) for i in range(3)], axis=-1)
    print(f"CLAHE output min: {result.min()}, max: {result.max()}")
    return result  

def load_single_tiff(directory, status_label, image_label):
    status_label.setText("Loading...")
    status_label.repaint()

    tif_stack = tif.imread(directory)
    _, num_channels, image_height, image_width = tif_stack.shape
    



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

    # Normalize the image to 0-1 range
    resized_image = resized_image.astype(np.float32) / np.max(resized_image)
    print(f"After normalization - min: {resized_image.min()}, max: {resized_image.max()}")  # Debug print

    # Adjust color balance
    red_channel = resized_image[:,:,0]
    green_channel = resized_image[:,:,1]
    blue_channel = resized_image[:,:,2]

    # Reduce green intensity
    green_reduction_factor = 0.4
    green_channel = green_channel * green_reduction_factor

    # Increase red and blue intensity
    red_increase_factor = 2.5
    blue_increase_factor = 6.0
    red_channel = np.clip(red_channel * red_increase_factor, 0, 1)
    blue_channel = np.clip(blue_channel * blue_increase_factor, 0, 1)

    # Reassemble the image
    adjusted_image = np.stack((red_channel, green_channel, blue_channel), axis=-1)
    print(f"After color adjustment - min: {adjusted_image.min()}, max: {adjusted_image.max()}")  # Debug print

    # Apply CLAHE for contrast enhancement
    adjusted_image = apply_clahe_rgb(adjusted_image, clip_limit=0.03)

    # Convert to 8-bit format
    adjusted_image = (adjusted_image * 255).astype(np.uint8)

    # Further brightness adjustment if needed
    brightness_factor = 1.2
    hsv = cv2.cvtColor(adjusted_image, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v * brightness_factor, 0, 255).astype(np.uint8)
    final_hsv = cv2.merge((h, s, v))
    brightened_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2RGB)

    plt.imshow(brightened_image)
    plt.title("Stitched Image")
    plt.axis('off')
    plt.imsave("stitched_image.png", brightened_image)

    print("Reading...")
    image = QImage("stitched_image.png")
    print("Setting up Pixmap")
    pixmap = QPixmap.fromImage(image)
    image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    status_label.setText("")




def get_grid_size(directory):
    max_x, max_y = 0, 0
    for _, x, y in file_generator(directory):
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    return (max_y + 1, max_x + 1)
