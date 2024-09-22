import imageio.v2 as imageio
import os
from tqdm import tqdm

### Creating and saving the animation
# Directory containing PNG files

parcels_file_name = "test"

directory = f'../data/{parcels_file_name}/'
print("Starting to work on the animation...")

# Get a list of PNG files in the directory
files = [file for file in os.listdir(directory) if file.endswith('.png')]
files.sort()  # Sort files in alphabetical order

# Create a list to store images
images = []

# Read images from files and append to the list
for file in tqdm(files, desc="Appending images"):
    img_path = os.path.join(directory, file)
    images.append(imageio.imread(img_path))
print("Gifing and MP4ing...")
# Save the animation
output_file = f'../data/{parcels_file_name}.gif'
imageio.mimsave(output_file, images, duration=10, loop=0)  # Adjust duration as needed
print("Created ", output_file)

# Save the animation as MP4
output_file = f'../data/{parcels_file_name}.mp4'
imageio.mimsave(output_file, images, fps=24)  # Adjust fps (frames per second) as needed
print("Created ", output_file)

print('Done')
