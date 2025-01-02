import os
import numpy as np
from skimage.transform import resize
import imageio.v3 as iio

# open images from dataset directory and resize them to 200,200,3

dataset_path = 'dataset/'
resized_path = 'resized/'
classes = []

# create resized directory if it doesn't exist
if not os.path.exists(resized_path):
    os.mkdir(resized_path)

    # create subdirectories in resized directory for each class
    for subdir in os.listdir(dataset_path):
        if not os.path.exists(resized_path + subdir):
            os.mkdir(resized_path + subdir)

# subdirectories in dataset directory are classes
for subdir in os.listdir(dataset_path):
    for file in os.listdir(dataset_path + subdir):
        if not os.path.exists(resized_path + subdir + '/' + file):
            try:
                img = iio.imread(dataset_path + subdir + '/' + file)
                img = resize(img, (200, 200, 3))
                img = np.array(img * 255, dtype=np.uint8)
                iio.imwrite(resized_path + subdir + '/' + file, img)
            except Exception as e:
                print(f'Error processing file: {file}, Error: {e}')
                try:
                    os.remove(file)
                    print(f'Removed corrupted or unreadable file: {file}')
                except Exception as remove_error:
                    print(f'Error removing file: {file}, Error: {remove_error}')
                    
    print(f'Class {subdir} processed.')

# Delete files with size 0KB or issues
for subdir in os.listdir(resized_path):
    resized_subdir_path = os.path.join(resized_path, subdir)
    for file in os.listdir(resized_subdir_path):
        file_path = os.path.join(resized_subdir_path, file)
        try:
            if os.path.getsize(file_path) == 0:  # Check if file size is 0KB
                os.remove(file_path)
                print(f'Removed 0KB file: {file_path}')
        except Exception as e:
            print(f'Error checking file: {file_path}, Error: {e}')

print("All processing and cleanup (removed 0 byte-size images) completed.")