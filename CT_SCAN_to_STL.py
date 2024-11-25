import os
import sys
import numpy as np
import SimpleITK as sitk
from skimage import measure
from stl import mesh
import matplotlib.pyplot as plt
from collections import Counter

############################################

def read_image_series(folder_path):
    # List all TIFF files in the folder
    tiff_files = [os.path.join(folder_path, f) for f in sorted(os.listdir(folder_path)) 
                  if f.lower().endswith('.tif') or f.lower().endswith('.tiff')]
    if not tiff_files:
        print("No TIFF files found in the specified folder.")
        sys.exit(1)
    
    # Read image series using SimpleITK
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(tiff_files)
    image = reader.Execute()
    
    return image

# ---------------------------------------------

def calculate_statistics(image):
    array = sitk.GetArrayFromImage(image)
    min_intensity = np.min(array)
    max_intensity = np.max(array)
    
    # Sample data for histogram to reduce memory usage
    sample_size = min(1000000, array.size)
    sample_indices = np.random.choice(array.size, size=sample_size, replace=False)
    sample_values = array.flatten()[sample_indices]
    counts = Counter(sample_values)
    most_common = counts.most_common(1)[0][0]
    
    print(f"Minimum intensity value: {min_intensity}")
    print(f"Maximum intensity value: {max_intensity}")
    print(f"Most common intensity value: {most_common}")
    
    # Optional: Plot histogram
    plt.hist(sample_values, bins=256, color='gray', alpha=0.7)
    plt.title('Pixel Intensity Distribution (Sampled Data)')
    plt.xlabel('Intensity Value')
    plt.ylabel('Frequency')
    plt.show()
    
    return min_intensity, max_intensity, most_common

# ---------------------------------------------

def generate_mesh(image, threshold):
    array = sitk.GetArrayFromImage(image)
    
    # Apply marching cubes
    verts, faces, normals, _ = measure.marching_cubes(array, level=threshold)
    return verts, faces

# ---------------------------------------------

def save_stl(verts, faces, output_path):
    # Create the mesh
    your_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            your_mesh.vectors[i][j] = verts[face[j], :]
    
    # Write to STL file
    your_mesh.save(output_path)
    print(f"STL file saved to {output_path}")

# ---------------------------------------------

def main():
    # Your specified paths
    folder_path = r"D:\Osmia bicornis\F3\reconstructed"
    output_path = r"D:\Osmia bicornis\F3\STL\output_model.stl"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Read the image series
    print("Reading image series...")
    image = read_image_series(folder_path)
    
    # Calculate statistics
    print("Calculating intensity statistics...")
    min_intensity, max_intensity, most_common = calculate_statistics(image)
    
    # Ask user for intensity threshold
    threshold = float(input(f"Enter the intensity value to use as threshold (between {min_intensity} and {max_intensity}): "))
    
    # Generate mesh
    print("Generating 3D mesh using marching cubes...")
    verts, faces = generate_mesh(image, threshold)
    
    # Save STL
    print("Saving STL file...")
    save_stl(verts, faces, output_path)
    
if __name__ == "__main__":
    main()
