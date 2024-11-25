import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from PIL import Image

####################

# Static variables for input folder and output directory
input_folder = r"D:\NN_2024_0014 Felipe Oliveira Ribas - Insects in gel&water May 2024 - Recosntructions\NN_2024_0014 Felipe Oliveira Ribas - Insects in gel&water May 2024 - Recosntructions\Batch I\Pot 3 - 28,29,30,31\recon"
output_dir = r"D:\NN_2024_0014 Felipe Oliveira Ribas - Insects in gel&water May 2024 - Recosntructions\NN_2024_0014 Felipe Oliveira Ribas - Insects in gel&water May 2024 - Recosntructions\Batch I\Pot 3 - 28,29,30,31\Filter"
output_format = 'tif'  # Choose either 'tif' or 'png'

# -------------------------------------

# Function to read TIFF images from a folder
def read_images_from_folder(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.tif') or f.endswith('.tiff')]
    image_files.sort()  # Ensure the order is consistent
    return image_files

# -------------------------------------

# Function to display an image and select a region to crop
def select_crop_region(image):
    fig, ax = plt.subplots(1)
    ax.imshow(image, cmap='gray')

    def onselect(eclick, erelease):
        global rect
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        width = x2 - x1
        height = y2 - y1
        side_length = max(abs(width), abs(height))
        rect = [(x1, y1), (x1 + side_length, y1 + side_length)] if width >= 0 else [(x1 - side_length, y1), (x1, y1 + side_length)]
    
    global rect
    rect = None
    rect_selector = RectangleSelector(ax, onselect, interactive=True)
    plt.show()
    return rect

# -------------------------------------

# Function to crop the selected region
def crop_image(image, rect):
    (x1, y1), (x2, y2) = rect
    cropped_image = image[y1:y2, x1:x2]
    return cropped_image

# -------------------------------------

# Main function
def main():
    image_files = read_images_from_folder(input_folder)
    
    if not image_files:
        print("No TIFF images found in the folder.")
        return

    # Select crop region on the first image
    first_image_path = os.path.join(input_folder, image_files[0])
    first_image = cv2.imread(first_image_path, cv2.IMREAD_UNCHANGED)
    
    if first_image is None:
        print(f"Failed to read the first image: {first_image_path}")
        return

    print(f"Displaying the first image for crop region selection: {first_image_path}")
    rect = select_crop_region(first_image)

    if rect is None:
        print("No region selected.")
        return

    # Apply the same crop region to all images
    for image_file in image_files:
        file_path = os.path.join(input_folder, image_file)
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        
        if image is None:
            print(f"Failed to read the image: {file_path}")
            continue

        cropped_image = crop_image(image, rect)
        output_filename = os.path.join(output_dir, f"cropped_{os.path.splitext(image_file)[0]}.{output_format}")
        cv2.imwrite(output_filename, cropped_image)
        print(f"Cropped image saved as: {output_filename}")

# -------------------------------------

if __name__ == "__main__":
    main()
