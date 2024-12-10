from PIL import Image

class Preview:
    def __init__(self):
        self.is_preview_landscape = 0
        self.preview_factor = 4

    def create_preview_image(self, image_paths, output_path):
        images = [Image.open(img_path) for img_path in image_paths]
        res_width = images[0].width
        res_height = images[0].height
        print(f"{res_width} x {res_height}")

        if self.is_preview_landscape:
            preview_image = Image.new('RGB', (res_width * 3, res_height))
            x_offset = 0
            for img in images:
                preview_image.paste(img, (x_offset, 0))
                x_offset += img.width
        else:
            preview_image = Image.new('RGB', (res_width, res_height * 3))
            y_offset = 0
            for img in images:
                preview_image.paste(img, (0, y_offset))
                y_offset += img.height

        preview_image = preview_image.resize((int(preview_image.width / self.preview_factor), int(preview_image.height / self.preview_factor)))
        preview_image.save(output_path)
        print(f"Preview image saved at: {output_path}")
