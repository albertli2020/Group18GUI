import os
import glob
from PIL import Image
import tifffile
from pathlib import Path

def convert_ome_tiff_to_tiff(input_folder, output_folder):
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    red_folder = os.path.join(output_folder, "red_channel")
    green_folder = os.path.join(output_folder, "green_channel")  
    blue_folder = os.path.join(output_folder, "blue_channel")
    
    Path(red_folder).mkdir(parents=True, exist_ok=True)
    Path(green_folder).mkdir(parents=True, exist_ok=True)
    Path(blue_folder).mkdir(parents=True, exist_ok=True)


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

            if len(single_frame.shape) >= 3 and single_frame.shape[-1] >= 3:
                # Image has color channels
                blue_channel = single_frame[0]
                green_channel = single_frame[1] 
                red_channel = single_frame[2]

                red_output = os.path.join(red_folder, f"{base_name}_red.tif")
                green_output = os.path.join(green_folder, f"{base_name}_green.tif")
                blue_output = os.path.join(blue_folder, f"{base_name}_blue.tif")
                
                tifffile.imwrite(red_output, red_channel, photometric='minisblack')
                tifffile.imwrite(green_output, green_channel, photometric='minisblack')
                tifffile.imwrite(blue_output, blue_channel, photometric='minisblack')
                
                print(f"  ├─ Red channel: {os.path.basename(red_output)}")
                print(f"  ├─ Green channel: {os.path.basename(green_output)}")
                print(f"  └─ Blue channel: {os.path.basename(blue_output)}")
                
            else:
                # Grayscale image
                print(f"  └─ Grayscale image detected, duplicating to all channels")
                
                red_output = os.path.join(red_folder, f"{base_name}_red.tif")
                green_output = os.path.join(green_folder, f"{base_name}_green.tif")
                blue_output = os.path.join(blue_folder, f"{base_name}_blue.tif")
                
                tifffile.imwrite(red_output, single_frame, photometric='minisblack')
                tifffile.imwrite(green_output, single_frame, photometric='minisblack')
                tifffile.imwrite(blue_output, single_frame, photometric='minisblack')


        
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