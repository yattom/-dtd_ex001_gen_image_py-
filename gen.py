import numpy as np
from PIL import Image


def generate_background(height, width) -> np.ndarray:
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


def save_image(background):
    # Create a Pillow Image object from the NumPy array
    image = Image.fromarray(background[:, :, :3], 'RGB')
    # Save the image to a file
    image.save("gradient_image.png")
    print("Image saved successfully.")


def main():
    # Define image dimensions
    width = 800
    height = 800
    background = generate_background(height, width)

    view = draw_cloud(background=background)

    save_image(view)


def draw_cloud(background: np.ndarray) -> np.ndarray:
    # Define dimensions of the volumetric space
    width = 100
    height = 100
    depth = 100

    # Create a 3D array to represent the volumetric space
    volumetric_space = np.zeros((width, height, depth))
    add_cloud(volumetric_space)

    view = render_view(background=background, space=volumetric_space)

    return view


def add_cloud(volumetric_space):
    width = volumetric_space.shape[0]
    height = volumetric_space.shape[1]
    depth = volumetric_space.shape[2]
    # Set density values in the volumetric space
    # For example, set a spherical cloud with density 1 in a certain region
    center_x, center_y, center_z = 50, 50, 50  # Center of the spherical cloud
    radius = 40  # Radius of the spherical cloud
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                distance_to_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2 + (z - center_z) ** 2)
                if distance_to_center < radius:
                    # Set density value to 1 within the sphere
                    volumetric_space[x, y, z] = 1


def render_view(background: np.ndarray, space: np.ndarray):
    view = np.zeros(shape=background.shape, dtype=background.dtype)
    for y in range(view.shape[1]):
        for x in range(view.shape[0]):
            c = background[x, y]

            space_x = int(space.shape[0] * x / view.shape[0])
            space_y = int(space.shape[1] * y / view.shape[1])
            for space_z in range(space.shape[2]):
                if space[space_x, space_y, space_z] != 0:
                    c = c * 0.99
            view[x, y] = c
    return view


if __name__=='__main__':
    main()
