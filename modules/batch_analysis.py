import os
import re
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from modules.image_analysis import analyze_image
import tifffile as tif

file_pattern = r"Pos(\d+)_(\d+)"

def postoindex(x, y, max_x, max_y):
    if y % 2 == 0:
        return y * max_x + x
    else:
        return (y + 1) * max_x - x - 1

def file_generator(directory):
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.ome.tif'):
            match = re.search(file_pattern, filename)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                yield (filename, x, y)

def process_image(args):
    filepath, img_index = args
    try:
        result = analyze_image(filepath, img_index)
        result['filename'] = os.path.basename(filepath)
        return result
    except Exception as e:
        return {'filename': os.path.basename(filepath), 'error': str(e)}

def run_batch_analysis(directory, grid_size, update_callback=None):
    max_x, max_y = grid_size
    file_list = []

    for filename, x, y in file_generator(directory):
        filepath = os.path.join(directory, filename)
        img_index = postoindex(x, y, max_x, max_y)
        if os.path.exists(filepath):
            file_list.append((filepath, img_index))

    results = []
    total_files = len(file_list)

    with ProcessPoolExecutor() as executor:
        future_to_file = {executor.submit(process_image, args): args for args in file_list}
        
        for i, future in enumerate(as_completed(future_to_file)):
            result = future.result()
            results.append(result)
            
            if update_callback:
                update_callback(result)
                update_callback({'progress': (i + 1) / total_files})

    # Save results to CSV
    csv_filepath = os.path.join(directory, 'batch_analysis_results.csv')
    with open(csv_filepath, mode='w', newline='') as file:
        fieldnames = ['filename', 'total_cells', 'green_cells', 'red_cells']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            if 'error' not in result:
                writer.writerow({k: result[k] for k in fieldnames})

    return results