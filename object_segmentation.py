import os
import cv2
import pandas as pd
import numpy as np
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo

# --- 1. CONFIGURATION ---
# Define your file paths and parameters here.
# IMPORTANT: Adjust these paths to match your local directory structure.
IMAGE_DIR = 'path/to/your/images'
GAZE_DATA_DIR = 'path/to/your/gaze_data'
OUTPUT_RESULTS_PATH = 'analysis_results.csv'

# Select a pre-trained Detectron2 model for instance segmentation.
# For high accuracy, Mask R-CNN is a solid choice.
# You can find more models in the Detectron2 Model Zoo: https://github.com/facebookresearch/detectron2/blob/main/MODEL_ZOO.md
CONFIG_FILE = "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"

# --- 2. SET UP DETECTRON2 PREDICTOR ---
print("Initializing Detectron2 model...")

# Get a default configuration and merge it with a pre-trained model's configuration.
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file(CONFIG_FILE))

# Set the model's weights from the Model Zoo.
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(CONFIG_FILE)

# Set a threshold for detection confidence. Objects with a score below this will be ignored.
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5

# Build the predictor.
predictor = DefaultPredictor(cfg)

print("Model loaded successfully.")

# --- 3. DATA PROCESSING PIPELINE ---
# Create an empty list to store the results of the analysis.
all_results =

# Get the list of all image and gaze data files.
image_files = sorted()
gaze_data_files = sorted()

if not image_files:
    print(f"No image files found in '{IMAGE_DIR}'. Please check your path.")
    exit()

if not gaze_data_files:
    print(f"No gaze data files found in '{GAZE_DATA_DIR}'. Please check your path.")
    exit()

# Loop through each image file to run the segmentation and analysis.
for image_filename in image_files:
    print(f"\nProcessing image: {image_filename}")
    image_path = os.path.join(IMAGE_DIR, image_filename)
    
    # Read the image using OpenCV.
    img = cv2.imread(image_path)
    if img is None:
        print(f"Warning: Could not read image at {image_path}. Skipping.")
        continue

    # Run the image through the Detectron2 model to get predictions.
    outputs = predictor(img)
    
    # Extract the detected instances from the output.
    instances = outputs["instances"]
    
    # Check if any objects were detected.
    if len(instances) == 0:
        print("No objects detected in this image. Skipping gaze analysis.")
        continue

    # Get the segmentation masks and class labels for each detected object.
    # The masks are returned as a binary array.[2, 3]
    pred_masks = instances.pred_masks.to('cpu').numpy()
    pred_classes = instances.pred_classes.to('cpu').numpy()

    # Loop through each participant's gaze data for the current image.
    for gaze_data_filename in gaze_data_files:
        # A simple check to match image and gaze data files.
        # This assumes a file naming convention like 'participant_1_image_name.csv'.
        if image_filename.split('.') in gaze_data_filename:
            print(f"  Analyzing gaze data from: {gaze_data_filename}")
            gaze_data_path = os.path.join(GAZE_DATA_DIR, gaze_data_filename)
            gaze_df = pd.read_csv(gaze_data_path)

            # Check if gaze data is available.
            if gaze_df.empty:
                print(f"    Warning: Gaze data file is empty. Skipping.")
                continue

            # Initialize a counter for each detected object instance.
            fixation_count_per_object = {}
            
            # --- 4. FUSING DATA: THE POINT-IN-MASK ALGORITHM ---
            # Loop through each gaze point in the participant's data.
            # Assuming the CSV has columns 'x_gaze' and 'y_gaze'.
            for index, row in gaze_df.iterrows():
                gaze_x = int(row['x_gaze'])
                gaze_y = int(row['y_gaze'])

                # Check for each detected object if the gaze point falls inside its mask.
                # This is a simple and efficient pixel-value lookup on the binary mask array.
                for mask_idx, mask in enumerate(pred_masks):
                    # Ensure coordinates are within image bounds before lookup.
                    if 0 <= gaze_y < mask.shape and 0 <= gaze_x < mask.shape[1]:
                        if mask[gaze_y, gaze_x]:
                            # If the gaze point is inside the mask, record the hit.
                            object_class_id = pred_classes[mask_idx]
                            object_instance_id = mask_idx # A unique ID for this specific object instance.
                            
                            key = f"{object_class_id}_{object_instance_id}"
                            fixation_count_per_object[key] = fixation_count_per_object.get(key, 0) + 1
                            
                            # Break the inner loop once a point is assigned to an object.
                            break

            # --- 5. AGGREGATE RESULTS ---
            # Store the final count for each object.
            for key, count in fixation_count_per_object.items():
                object_class_id, object_instance_id = key.split('_')
                
                # Get the class name from Detectron2's metadata.
                class_name = cfg.DATASETS.TRAIN.get('thing_classes', ['Unknown'])[int(object_class_id)]
                
                results = {
                    'image_filename': image_filename,
                    'participant_id': gaze_data_filename.split('_'),
                    'object_class_id': object_class_id,
                    'object_class_name': class_name,
                    'object_instance_id': object_instance_id,
                    'fixation_count': count
                }
                all_results.append(results)

# --- 6. SAVE RESULTS TO CSV ---
if all_results:
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(OUTPUT_RESULTS_PATH, index=False)
    print(f"\nAnalysis complete. Results saved to '{OUTPUT_RESULTS_PATH}'.")
else:
    print("\nNo analysis results to save. Please check your data and paths.")
