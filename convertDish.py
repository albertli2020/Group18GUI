import os
import glob
from PIL import Image
import tifffile
from pathlib import Path

def convert_ome_tiff_to_tiff(input_folder, output_folder):
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    pattern1 = os.path.join(input_folder, "*.ome.tif")
    pattern2 = os.path.join(input_folder, "*.ome.tiff")
    pattern3 = os.path.join(input_folder, "*.OME.TIF")
    pattern4 = os.path.join(input_folder, "*.OME.TIFF")
    
    ome_files = []
    for pattern in [pattern1, pattern2, pattern3, pattern4]:
        ome_files.extend(glob.glob(pattern))
    
    if not ome_files:
        print(f"No .ome.tif files found in {input_folder}")
        return
    
    print(f"Found {len(ome_files)} .ome.tif files to convert")
    
    ome_stack = ome_files[0]    

    with tifffile.TiffFile(ome_stack) as tif:
        image_data = tif.asarray()
        for index, fov in enumerate(ome_files):
            single_frame = image_data[index]
            base_name = Path(fov).stem
            output_file = os.path.join(output_folder, f"{base_name}.tif")
            tifffile.imwrite(output_file, single_frame, photometric='minisblack')
            print(f"✓ Converted: {os.path.basename(fov)} -> {os.path.basename(output_file)}")

        
def main():
    current_directory_os = os.getcwd()

    input_folder = os.path.join(current_directory_os, "omeFolder")  # Change this to your input folder path
    output_folder = os.path.join(current_directory_os, "convertedTiffs")   # Change this to your output folder path
        
    print("OME-TIFF to TIFF Converter")
    print("=" * 40)
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print("=" * 40)
    
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist!")
        print("Please modify the input_folder variable in the script.")
        return
    
    convert_ome_tiff_to_tiff(input_folder, output_folder)

if __name__ == "__main__":
    main()