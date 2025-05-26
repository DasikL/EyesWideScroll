#fix some naming errors
import os

for filename in os.listdir("current_images"):
    if filename.endswith("..jpg"):
        new_filename = filename.replace("..jpg", ".jpg")
        os.rename(os.path.join("current_images", filename), os.path.join("current_images", new_filename))