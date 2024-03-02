import numpy as np
from PIL import Image

# Define image dimensions
width = 800
height = 600

# Create a NumPy array representing the image data
# In this example, we'll create a gradient image
# You can generate any image data you desire here
image_data = np.zeros((height, width, 3), dtype=np.uint8)

# Generate a gradient from black to white horizontally
for y in range(height):
    for x in range(width):
        r = int((x / width) * 255)  # Red component
        b = int(((width - x) / width) * 255)  # Blue component

        # Set the pixel color
        image_data[y, x] = [r, 0, b]  # Red, Green, Blue

# Create a Pillow Image object from the NumPy array
image = Image.fromarray(image_data)

# Save the image to a file
image.save("gradient_image.png")

print("Image saved successfully.")
