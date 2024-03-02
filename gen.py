import numpy as np
from PIL import Image

# Define image dimensions
width = 800
height = 600

# Create arrays for black-to-red and blue-to-black gradients
black_to_red = np.zeros((height, width, 4), dtype=np.uint8)
blue_to_black = np.zeros((height, width, 4), dtype=np.uint8)

# Generate black-to-red gradient
for y in range(height):
    for x in range(width):
        black_to_red[y, x] = [255, 0, 0, int(x / width * 255)]

# Generate blue-to-black gradient
for y in range(height):
    for x in range(width):
        blue_to_black[y, x] = [0, 0, 255, int((width - x) / width * 255)]

# Create a blended gradient using alpha blending
alpha_channel_normalized = blue_to_black[:, :, 3] / 255.0  # Normalize alpha channel
blended_gradient = black_to_red.copy()  # Initialize with black-to-red gradient

# Apply alpha blending

blended_gradient[:, :, :3] = (blended_gradient[:, :, :3] * (1.0 - alpha_channel_normalized[:, :, None]) +
                              blue_to_black[:, :, :3] * alpha_channel_normalized[:, :, None]).astype(np.uint8)

# Create a Pillow Image object from the NumPy array
image = Image.fromarray(blended_gradient[:, :, :3], 'RGB')

# Save the image to a file
image.save("gradient_image.png")

print("Image saved successfully.")
