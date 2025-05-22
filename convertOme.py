import os
from tifffile import imread, imwrite

def convert_ome_tiff_to_tiff(input_path, output_path):
    #Converts an OME-TIFF file to a standard TIFF file.

    try:
        image_data = imread(input_path)

        imwrite(output_path, image_data)
        print(f"Successfully converted '{input_path}' to '{output_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")

current_directory_os = os.getcwd()


input_file = current_directory_os + "/post stain dapi, iba1, gfap_2_MMStack_6-Pos000_001.ome.tif"
output_file = current_directory_os + "/output.tif"
convert_ome_tiff_to_tiff(input_file, output_file)
