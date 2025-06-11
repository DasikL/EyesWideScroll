import os
path = "C:/EWS/Eyetracker/new_images/"

for filename in os.listdir(path):
    
    file_id = str(filename.split("_")[0]).strip("id")
    file_id_zeroes = "0" * (3 - len(file_id))+ file_id
    file_coda_list = filename.split("_")[1:len(filename.split("_"))-1]
    file_coda = "_"
    for chunk in file_coda_list:
        file_coda += chunk + "_"
    new_filename = f"id"+file_id_zeroes+str(file_coda)+".jpg"
    os.rename(os.path.join(path, filename), os.path.join(path, new_filename))
    