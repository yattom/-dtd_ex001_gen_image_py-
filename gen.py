import numpy as np
from PIL import Image



def main():
    # Define image dimensions
    width = 800
    height = 600
    background = generate_background(height, width)
    # Create a Pillow Image object from the NumPy array
    image = Image.fromarray(background[:, :, :3], 'RGB')
    # Save the image to a file
    image.save("gradient_image.png")
    print("Image saved successfully.")


def generate_background(height, width):
    # Create arrays for black-to-red and blue-to-black gradients
    red = np.zeros((height, width, 4), dtype=np.uint8)
    blue = np.zeros((height, width, 4), dtype=np.uint8)
    # Generate black-to-red gradient
    for y in range(height):
        for x in range(width):
            red[y, x] = [255, 0, 0, int(x / width * 255)]
    # Generate blue-to-black gradient
    for y in range(height):
        for x in range(width):
            blue[y, x] = [0, 0, 255, int((width - x) / width * 255)]
    # Create a blended gradient using alpha blending
    blue_alpha = blue[:, :, 3] / 255.0  # Normalize alpha channel
    red_alpha = red[:, :, 3] / 255.0  # Normalize alpha channel
    blended_gradient = np.zeros((height, width, 3), dtype=np.uint8)
    # Apply alpha blending
    blended_gradient[:, :, :3] = (red[:, :, :3] * (red_alpha[:, :, None]) +
                                  blue[:, :, :3] * blue_alpha[:, :, None]).astype(np.uint8)
    return blended_gradient


if __name__=='__main__':
    main()
