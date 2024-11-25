
import os
import numpy as np
from PIL import Image

################

def get_required_images(folder_path, grid_size):
    required_images = grid_size[0] * grid_size[1]
    valid_images = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.tiff', '.tif', '.bmp', '.png')):  # Include BMP files
            file_path = os.path.join(folder_path, filename)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
            
            #if file_size_mb > 1:  # Assuming 1MB as the min size
            valid_images.append(file_path)
            
            if len(valid_images) >= required_images:
                break
    
    return valid_images[:required_images]

# ---------------------------------------

def load_and_normalize_images(image_paths, resize_factor=1.0):
    images = []
    global_min = float('inf')
    global_max = float('-inf')

    # First pass: Determine global min and max
    for file_path in image_paths:
        try:
            img = Image.open(file_path)
            print(f"Original image mode: {img.mode}, size: {img.size}")  # Debug print

            # Ensure image is in 16-bit mode, or convert to 8-bit if BMP
            if img.mode != 'I;16':
                img = img.convert('I;16' if file_path.lower().endswith(('.tiff', '.tif', '.png')) else 'L')

            img_array = np.array(img)
            min_val = np.min(img_array)
            max_val = np.max(img_array)
            print(f"Image: {os.path.basename(file_path)}, min={min_val}, max={max_val}")  # Debug print

            if min_val < global_min:
                global_min = min_val
            if max_val > global_max:
                global_max = max_val
        except (IOError, SyntaxError) as e:
            print(f"File {file_path} could not be opened or is not a valid image: {e}")

    print(f"Global min: {global_min}, Global max: {global_max}")  # Debug print

    # Second pass: Load and normalize images
    for file_path in image_paths:
        try:
            img = Image.open(file_path)
            img = img.convert('I;16' if file_path.lower().endswith(('.tiff', '.tif', '.png')) else 'L')
            img_array = np.array(img)

            # Normalize to [0, 1] range based on global min and max
            img_normalized = (img_array - global_min) / (global_max - global_min)
            img_8bit = (img_normalized * 255).astype(np.uint8)

            img = Image.fromarray(img_8bit)

            if resize_factor != 1.0:
                new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
                img = img.resize(new_size, Image.BICUBIC)
                img_8bit = np.array(img)

            images.append(img_8bit)
            print(f"Loaded and processed image: {os.path.basename(file_path)}, shape: {img_8bit.shape}")  # Debug print
        except (IOError, SyntaxError) as e:
            print(f"File {file_path} could not be opened or is not a valid image: {e}")

    print(f"Found {len(images)} valid images.")  # Debugging print statement

    if not images:
        return np.array([])

    # Stack images into a 3D numpy array
    slices = np.stack(images, axis=0)

    norm_min_val = np.min(slices)
    norm_max_val = np.max(slices)
    print(f"After normalization: min={norm_min_val}, max={norm_max_val}")  # Debug print

    return slices

# ---------------------------------------

def save_slices_as_grid_image(normalized_data, output_path, grid_size):
    if normalized_data.size == 0:
        print("No valid images to create a grid.")
        return

    num_slices = normalized_data.shape[0]
    slice_height, slice_width = normalized_data.shape[1:3]

    print(f"Grid image size: {slice_width * grid_size[1]}x{slice_height * grid_size[0]}")  # Debug print
    
    # Create an empty image for the grid
    grid_image = Image.new('L', (slice_width * grid_size[1], slice_height * grid_size[0]))

    for i in range(num_slices):
        row = i // grid_size[1]
        col = i % grid_size[1]

        if row >= grid_size[0]:
            break

        slice_data = normalized_data[i, :, :]
        slice_image = Image.fromarray(slice_data)
        grid_image.paste(slice_image, (col * slice_width, row * slice_height))
        print(f"Pasted image at row {row}, col {col}")  # Debug print

    grid_image.save(output_path)
    print(f"Grid image saved to {output_path}")

    # Load the saved image for verification
    saved_image = Image.open(output_path)
    saved_array = np.array(saved_image)
    print(f"Saved image size: {saved_image.size}, min={np.min(saved_array)}, max={np.max(saved_array)}")
    saved_image.show()

# ---------------------------------------

def main(input_folder, output_image_path, grid_size, resize_factor=1.0):
    image_paths = get_required_images(input_folder, grid_size)
    if not image_paths:
        print("No valid images found to create a grid.")
        return

    print(f"Number of images to load: {len(image_paths)}")  # Debug print
    normalized_data = load_and_normalize_images(image_paths, resize_factor=resize_factor)
    save_slices_as_grid_image(normalized_data, output_image_path, grid_size)

# ---------------------------------------

if __name__ == "__main__":
    input_folder = r"D:\PHD BELGIUM\PROJECTS\Insects_Simulations\1_Project_CT_Scans\SAMPLES\A3_A8\recon"
    output_image_path = r"D:\PHD BELGIUM\PROJECTS\Insects_Simulations\1_Project_CT_Scans\SAMPLES\A3_A8\recon\output_grid_bombus.png"  # Add file extension
    grid_size = (23,23)  # Adjust grid size as needed
    resize_factor = 0.4  # Resize factor to reduce image dimensions (e.g., 0.5 for 50% size)

    main(input_folder, output_image_path, grid_size, resize_factor=resize_factor)
