#import csv reading
import os
import csv
import pandas as pd

durations_df = pd.DataFrame(columns=['participant_id', 'file_name', 'image_name', 'system_time_diff_seconds', 'device_time_diff_seconds'])
# current directory
for file in os.listdir('.'):
    if file.startswith("Proband") and not "Valididitätskontrolle" in file and file.endswith('.csv'):
        current_frame = pd.read_csv(file, sep=',')
        device_start_time = current_frame['device_time_stamp'].iloc[0]
        device_end_time = current_frame['device_time_stamp'].iloc[-1]
        device_time_diff = device_end_time - device_start_time
        system_start_time = current_frame['system_time_stamp'].iloc[0]
        system_end_time = current_frame['system_time_stamp'].iloc[-1]
        system_time_diff = system_end_time - system_start_time
        current_times = {
            'participant_id': [file.strip("Proband").split('_')[0]], 
            'file_name': [file],
            # image_name is the file name from id... onwards
            #e.g. Proband53_15_41_08_id088_politik -> id088_politik
            'image_name': [file[(file.index("id")):].strip('.csv')+".jpg"],
            'system_time_diff_seconds': [system_time_diff/1000000],
            'device_time_diff_seconds': [device_time_diff/1000000]}
        current_times_df = pd.DataFrame(current_times)
        durations_df = pd.concat([durations_df,current_times_df], ignore_index=True)
        print(file)
#save duration_df to csv
durations_df.to_csv('view_durations.csv', index=False)
