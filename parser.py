#fix some naming errors
import os

for filename in os.listdir("new_images"):
    if filename.endswith("_i.jpg"):
        new_filename = filename.replace("_i.jpg", "_.jpg")
        os.rename(os.path.join("new_images", filename), os.path.join("new_images", new_filename))