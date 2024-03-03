from dataclasses import dataclass
from random import randint

import numpy as np
from PIL import Image

meter = float


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
    height = 600
    background = generate_background(height, width)

    view = draw_cloud(background=background)

    save_image(view)


def draw_cloud(background: np.ndarray) -> np.ndarray:
    # Define dimensions of the volumetric space
    width = 100
    height = 100
    depth = 100

    # Create a 3D array to represent the volumetric space
    volumetric_space = np.zeros((width, height, depth, 2), dtype=np.float32)
    add_cloud(volumetric_space)
    light_cloud(volumetric_space)

    # Define the viewport
    viewport = Viewport(position=Vector(50, 50, -100),
                        vector=Vector(0, 0, 1),
                        focal_length=0.1,
                        projection_plane_size=RectSize(width=0.1, height=0.075),
                        image_size=RectSize(width=100, height=75))
    view = render_view(viewport=viewport, background=background, space=volumetric_space)

    return view


def add_cloud(volumetric_space):
    width = volumetric_space.shape[0]
    height = volumetric_space.shape[1]
    depth = volumetric_space.shape[2]
    # Set density values in the volumetric space
    # For example, set a spherical cloud with density 1 in a certain region
    for i in range(3):
        center_x, center_y, center_z = randint(0, width), randint(0, height), randint(50, depth)
        radius = randint(5, 30)  # Radius of the spherical cloud
        for z in range(max(0, center_z - radius), min(center_z + radius, depth)):
            for y in range(max(0, center_y - radius), min(center_y + radius, height)):
                for x in range(max(0, center_x - width), min(center_x + radius, width)):
                    distance_to_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2 + (z - center_z) ** 2)
                    if distance_to_center < radius:
                        # Set density value to 1 within the sphere
                        volumetric_space[x, y, z][0] = 1


def light_cloud(volumetric_space):
    width = volumetric_space.shape[0]
    height = volumetric_space.shape[1]
    depth = volumetric_space.shape[2]
    for x in range(width):
        for z in range(depth):
            light = 1.0
            for y in range(height):
                if volumetric_space[x, y, z][0] == 1:
                    volumetric_space[x, y, z][1] = light
                    light *= 0.95


@dataclass
class Vector:
    x: meter
    y: meter
    z: meter

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
    width: meter
    height: meter


@dataclass
class Viewport:
    position: Vector
    vector: Vector
    focal_length: meter
    projection_plane_size: RectSize
    image_size: RectSize = RectSize


def add_white(base, intensity):
    return np.array([min(255, base[0] + 255 * 0.1 * intensity),
                     min(255, base[1] + 255 * 0.1 * intensity),
                     min(255, base[2] + 255 * 0.1 * intensity)])


def render_view(viewport: Viewport, background: np.ndarray, space: np.ndarray):
    viewport_center = viewport.position - viewport.vector * viewport.focal_length
    viewport_left_top = viewport_center - Vector(viewport.projection_plane_size.width / 2,
                                                 viewport.projection_plane_size.height / 2, 0)

    rendered_image = np.zeros(shape=(viewport.image_size.height, viewport.image_size.width, 3),
                              dtype=np.uint8)
    image_width = viewport.image_size.width
    image_height = viewport.image_size.height
    pixel_x_v = Vector(viewport.projection_plane_size.width / image_width, 0, 0)
    pixel_y_v = Vector(0, viewport.projection_plane_size.height / image_height, 0)

    for y in range(image_height):
        print(f"{y=} / {image_height}")
        for x in range(image_width):
            pixel_position = pixel_x_v * x + pixel_y_v * y + viewport_left_top
            ray_direction = (viewport.position - pixel_position).normalize()

            # calc color for pixel[x, y]
            c = background[x, y]

            for i in range(200):
                point = viewport.position + ray_direction * i
                if not (0 <= point.x < 100 and 0 <= point.y < 100 and 0 <= point.z < 100):
                    continue
                try:
                    if space[int(point.x), int(point.y), int(point.z)][0] != 0:
                        c = c * 0.99
                    if space[int(point.x), int(point.y), int(point.z)][1] != 0:
                        c = add_white(c, space[int(point.x), int(point.y), int(point.z)][1])
                except IndexError:
                    pass
            rendered_image[image_height - y - 1, x] = c
    return rendered_image


if __name__ == '__main__':
    main()
