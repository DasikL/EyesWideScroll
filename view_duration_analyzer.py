#aggregates view duration data
# measures view duration for stimuli and participants
# analyzes view duration patterns for grouped data
import pandas as pd
import matplotlib.pyplot as plt

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

#plot system_time_diff_seconds with different lines for each participant for all images by increasing id on the x-axis

for participant_id in range(1,10):
    participant_data = view_duration_df[view_duration_df['participant_id'] == participant_id]
    print(f"Participant {participant_id} Data:\n", participant_data)
    plt.plot(participant_data['image_name'], participant_data['system_time_diff_seconds'], label=f'Participant {participant_id}')
    
plt.xlabel('Image Name')
plt.ylabel('System Time Diff (seconds)')
plt.title(f'System Time Diff for Participant {participant_id}')
plt.xticks(rotation=90)
plt.show()