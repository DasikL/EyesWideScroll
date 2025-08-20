#aggregates view duration data
# measures view duration for stimuli and participants
# analyzes view duration patterns for grouped data
import pandas as pd

view_duration_df = pd.read_csv('view_durations.csv')

#Test: should be between 5-15
print("lowest Duration: ",view_duration_df["system_time_diff_seconds"].min())
# --> !!
print("highest Duration: ",view_duration_df["system_time_diff_seconds"].max())

#---General statistics
print("Mean Duration: ",view_duration_df["system_time_diff_seconds"].mean())
print("Median Duration: ",view_duration_df["system_time_diff_seconds"].median())

#--Group by image_name
grouped_by_image = view_duration_df.groupby('image_name').agg({
    'system_time_diff_seconds': ['mean', 'median', 'min', 'max'],
    'device_time_diff_seconds': ['mean', 'median', 'min', 'max'],
    'participant_id': 'count'
}).reset_index()
print(grouped_by_image.head())

#--Group by participant_id
#--Group by tag