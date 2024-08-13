import os
import re
import tifffile as tif
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

def postoindex(x, y, max_x, max_y):
    if y % 2 == 0:
        return y * max_y + x
    else:
        return (y // 2 + 1) * (max_x + max_y) - x - 1

file_pattern = r"Pos(\d+)_(\d+)"
def file_generator(base_dir):
    for filename in sorted(os.listdir(base_dir)):
        if filename.endswith('.ome.tif'):
            match = re.search(file_pattern, filename)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                yield (filename, x, y)

def load_and_stitch_tiffs(directory, status_label, image_label):
    status_label.setText("Stitching...")
    status_label.repaint()

    positions = [] 

    max_x, max_y = 0, 0
    for filename, x, y in file_generator(directory):
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        positions.append((x, y)) 
    
    sample_tiff = os.path.join(directory, sorted(os.listdir(directory))[4])
    print(sample_tiff)
    sample_img = tif.imread(sample_tiff) 
    image_shape = sample_img.shape[1:] 
    print(image_shape)

    stitched_blue_channel = np.zeros(((max_y + 1) * image_shape[1], (max_x + 1) * image_shape[2]), dtype=np.uint16)
    stitched_green_channel = np.zeros_like(stitched_blue_channel)
    stitched_red_channel = np.zeros_like(stitched_blue_channel)
    
    for filename, x, y in file_generator(directory):
        file_path = os.path.join(directory, filename)
        img = tif.imread(file_path)
        index = postoindex(x, y, max_x, max_y)
        if img[index].ndim == 3 and img.shape[1:][0] == 3:
            blue_channel = img[index][0]
            green_channel = img[index][1]
            red_channel = img[index][2]
        else:
            raise ValueError(f"Unexpected number of channels in {filename}")
        
        stitched_y = max_y - y
        stitched_x = x

        stitched_blue_channel[stitched_y * image_shape[1]:(stitched_y + 1) * image_shape[1],
                            stitched_x * image_shape[2]:(stitched_x + 1) * image_shape[2]] = blue_channel

        stitched_green_channel[stitched_y * image_shape[1]:(stitched_y + 1) * image_shape[1],
                            stitched_x * image_shape[2]:(stitched_x + 1) * image_shape[2]] = green_channel

        stitched_red_channel[stitched_y * image_shape[1]:(stitched_y + 1) * image_shape[1],
                            stitched_x * image_shape[2]:(stitched_x + 1) * image_shape[2]] = red_channel
            

    # Combine the channels into one image (RGB)
    stitched_image = np.stack([stitched_red_channel, stitched_green_channel, stitched_blue_channel], axis=-1)

    # Convert numpy array to QImage
    height, width, _ = stitched_image.shape
    qimage = QImage(stitched_image.data, width, height, 3 * width, QImage.Format.Format_RGB888)

    # Display the stitched image in the QLabel
    pixmap = QPixmap.fromImage(qimage)
    image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    # Clear the status label
    status_label.setText("")