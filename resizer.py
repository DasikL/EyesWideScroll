import os
from PIL import Image

# === Configuration ===
input_folder = r'C:\EWS\Webcomics\Arcade_Rage'  # Change this path
output_folder = os.path.join(input_folder, 'resized')
target_size = (800, 800)

# === Ensure output folder exists ===
os.makedirs(output_folder, exist_ok=True)

# === Supported image extensions ===
valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}

def center_crop(im):
    width, height = im.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    return im.crop((left, top, right, bottom))

# === Process all images ===
for filename in os.listdir(input_folder):
    if os.path.splitext(filename.lower())[1] in valid_extensions:
        try:
            img_path = os.path.join(input_folder, filename)
            with Image.open(img_path) as img:
                img = img.convert("RGB")  # Normalize format
                img = center_crop(img)
                img = img.resize(target_size, Image.LANCZOS)

                output_path = os.path.join(output_folder, filename)
                img.save(output_path)
                print(f"Resized: {filename}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")