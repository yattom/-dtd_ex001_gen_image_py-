from dataclasses import dataclass

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

    # Define the viewport
    viewport = Viewport(position=Vector(50, 50, 0), vector=Vector(0, 0, 1), focal_length=100,
                        view_image_size=RectSize(width=800, height=800))
    view = render_view(viewport=viewport, background=background, space=volumetric_space)

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


@dataclass
class Vector:
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scale):
        return Vector(self.x * scale, self.y * scale, self.z * scale)

    def normalize(self):
        mag = np.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        return Vector(self.x / mag, self.y / mag, self.z / mag)


@dataclass
class RectSize:
    width: int
    height: int


@dataclass
class Viewport:
    position: Vector
    vector: Vector
    focal_length: float
    view_image_size: RectSize


def render_view(viewport: Viewport, background: np.ndarray, space: np.ndarray):
    viewport_center = viewport.position + viewport.vector * viewport.focal_length

    rendered_image = np.zeros(shape=(viewport.view_image_size.height, viewport.view_image_size.width, 3),
                              dtype=np.uint8)
    for y in range(rendered_image.shape[1]):
        for x in range(rendered_image.shape[0]):
            pixel_world_x = (x - viewport.view_image_size.width / 2) * (800 / viewport.view_image_size.width)
            pixel_world_y = (y - viewport.view_image_size.height / 2) * (800 / viewport.view_image_size.height)
            pixel_position = Vector(pixel_world_x, pixel_world_y, viewport_center.z)
            ray_direction = (pixel_position - viewport.position).normalize()

            # calc color for pixel[x, y]
            c = background[x, y]

            for i in range(100):
                point = viewport.position + ray_direction * i
                try:
                    if space[int(point.x), int(point.y), int(point.z)] != 0:
                        c = c * 0.99
                except IndexError:
                    pass
            rendered_image[x, y] = c
    return rendered_image


if __name__ == '__main__':
    main()
