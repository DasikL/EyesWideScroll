#aggregates view duration data
# measures view duration for stimuli and participants
# analyzes view duration patterns for grouped data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
view_duration_df = pd.read_csv('view_durations.csv')

#Test: should be between 5-15
print("lowest Duration: ",view_duration_df["system_time_diff_seconds"].min())
# --> !!
print("highest Duration: ",view_duration_df["system_time_diff_seconds"].max())

#---General statistics
print("Mean Duration: ",view_duration_df["system_time_diff_seconds"].mean())
print("Median Duration: ",view_duration_df["system_time_diff_seconds"].median())
#each image name is formatted like id<image_id>_<tag1_<tag2>..._.jpg
#image_tag_dictionary should contain a list of tags for every image
#group view_durations_df by image id and dissect image_name
image_tag_dict = {}
for file in view_duration_df['image_name']:
    tags = file.split('_')[1:-1]  # Exclude 'id' and '.jpg'
    if "ncc" in tags:
        tags.remove("ncc")
    
    image_id = int(file.split('_')[0][2:])  # Extract image_id from 'id<image_id>'
    if len(tags)<1:
        #error in image namng - bandaid solution
        image_tag_dict[image_id] = ["text"]
    else:
        image_tag_dict[image_id] = tags
print("image_tag_dict", image_tag_dict)
#--Group by image_name

#--Group by participant_id
#--Group by tag

#plot system_time_diff_seconds with different lines for each participant for all images by increasing id on the x-axis
def plot_participants():
    for participant_id in range(1,10):
        participant_data = view_duration_df[view_duration_df['participant_id'] == participant_id]
        print(f"Participant {participant_id} Data:\n", participant_data)
        plt.plot(participant_data['image_id'], participant_data['system_time_diff_seconds'], label=f'Participant {participant_id}')
        
    plt.xlabel('Image Name')
    plt.ylabel('System Time Diff (seconds)')
    plt.title(f'System Time Diff for Participant {participant_id}')
    plt.xticks(rotation=90)
    plt.show()

def view_duration_images():
    grouped_by_image = view_duration_df.groupby('image_id').agg({
        'system_time_diff_seconds': ['mean', 'median', 'min', 'max'],
        'device_time_diff_seconds': ['mean', 'median', 'min', 'max']
    }).reset_index()
    return grouped_by_image
print("view duration images",view_duration_images().head())
#plot view duration for images with image id on the x-axis and median view duration on the y-axis
def plot_view_duration_images():
    image_data = view_duration_images()
    plt.bar(image_data['image_id'], image_data['system_time_diff_seconds']['median'])
    plt.xlabel('Image ID')
    plt.ylabel('Median System Time Diff (seconds)')
    plt.title('Median System Time Diff for Images')
    plt.show()
plot_view_duration_images()

#print id and median time of image that is the minimum of median system_time_diff_seconds
min_image = view_duration_images().sort_values(by=('system_time_diff_seconds', 'median')).iloc[0]
max_image = view_duration_images().sort_values(by=('system_time_diff_seconds', 'median')).iloc[-1]
print("Image ID with Minimum Median System Time Diff (seconds):", min_image['image_id'])
print("Minimum Median System Time Diff (seconds):", min_image['system_time_diff_seconds']['median'])
print("Image ID with Maximum Median System Time Diff (seconds):", max_image['image_id'])
print("Maximum Median System Time Diff (seconds):", max_image['system_time_diff_seconds']['median'])

def analyze_tag_groups():
    # Create a dictionary to group images by their tag combinations
    tag_group_dict = {}
    
    # Group images by their tag combinations
    for image_id, tags in image_tag_dict.items():
        tag_combination = tuple(sorted(tags))  # Use sorted tuple for consistent grouping
        if tag_combination not in tag_group_dict:
            tag_group_dict[tag_combination] = []
        tag_group_dict[tag_combination].append(image_id)
    
    # Analyze each tag group
    tag_group_analysis = []
    
    for tag_combination, image_ids in tag_group_dict.items():
        # Filter data for images in this tag group
        tag_group_data = view_duration_df[view_duration_df['image_id'].isin(image_ids)]
        
        if not tag_group_data.empty:
            analysis = {
                'tag_combination': tag_combination,
                'tag_string': '_'.join(tag_combination),  # For easier reading
                'image_ids': image_ids,
                'image_count': len(image_ids),
                'total_observations': len(tag_group_data),
                'mean_system_time': tag_group_data['system_time_diff_seconds'].mean(),
                'median_system_time': tag_group_data['system_time_diff_seconds'].median(),
                'std_system_time': tag_group_data['system_time_diff_seconds'].std(),
                'min_system_time': tag_group_data['system_time_diff_seconds'].min(),
                'max_system_time': tag_group_data['system_time_diff_seconds'].max()
            }
            tag_group_analysis.append(analysis)
    
    # Convert to DataFrame for easier analysis
    tag_analysis_df = pd.DataFrame(tag_group_analysis)
    
    # Sort by mean system time
    tag_analysis_df = tag_analysis_df.sort_values('mean_system_time', ascending=False)
    print("tag_analysis1", tag_analysis_df)
    return tag_analysis_df

# Usage and display
def display_tag_group_analysis():
    tag_analysis = analyze_tag_groups()
    
    print("\n" + "="*80)
    print("TAG GROUP ANALYSIS")
    print("="*80)
    
    print(f"Total tag groups found: {len(tag_analysis)}")
    print("\nTag groups ranked by mean viewing time:")
    print("-" * 80)
    
    for idx, row in tag_analysis.iterrows():
        print(f"Tag Group: {row['tag_string']}")
        print(f"  Images: {row['image_count']} (IDs: {row['image_ids']})")
        print(f"  Observations: {row['total_observations']}")
        print(f"  Mean time: {row['mean_system_time']:.2f}s")
        print(f"  Median time: {row['median_system_time']:.2f}s")
        print(f"  Std dev: {row['std_system_time']:.2f}s")
        print(f"  Range: {row['min_system_time']:.2f}s - {row['max_system_time']:.2f}s")
        print("-" * 40)
    
    return tag_analysis

# Run the analysis
tag_analysis_results = display_tag_group_analysis()

# Plot tag groups by mean viewing time
def plot_tag_groups():
    tag_analysis = analyze_tag_groups()
    
    plt.figure(figsize=(12, 8))
    plt.barh(range(len(tag_analysis)), tag_analysis['mean_system_time'])
    plt.yticks(range(len(tag_analysis)), tag_analysis['tag_string'])
    plt.xlabel('Mean System Time Diff (seconds)')
    plt.title('Mean Viewing Time by Tag Group')
    plt.tight_layout()
    plt.show()
def analyze_temporal_pattern():
    # for every participant, sort their viewing data by time 
    # every file name is formatted like this: Proband<probandID>_hour_minute_seconds_id<imgID>_tag1_tag2..._.csv

    for participant_id, group in view_duration_df.groupby('participant_id'):

        group = group.sort_values('timestamp')
        print(group)
        # plot the system time diff for each image
        plt.figure(figsize=(12, 6))
        plt.plot(group['timestamp'], group['system_time_diff_seconds'], marker='o')
        plt.title(f"Viewing Time Pattern for Participant {participant_id}")
        plt.xlabel('Timestamp')
        plt.ylabel('System Time Diff (seconds)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

plot_tag_groups()
#analyze_temporal_pattern()

def create_view_time_matrix():
    # Create a matrix with semantic categories on the one axis and text/no-text on the other axis
    # images with text are marked with the tag textimg, images with text only are marked with the tag text
    semantic_categories = ["meme", "person", "politik", "ort"]
    tag_analysis_df = analyze_tag_groups()

    # Create the view time matrix
    view_time_matrix = pd.DataFrame(0, index=semantic_categories, columns=["text", "no_text"], dtype=int)
    print("tag analysis",tag_analysis_df)
    # for every tag combination in tag_analysis_df["tag_combination"]

    for idx, row in tag_analysis_df.iterrows():
        for category in semantic_categories:
            if category in row['tag_string']:
                if 'textimg' in row['tag_string']:
                    view_time_matrix.at[category, "text"] = row['median_system_time']
                elif 'textigm' in row['tag_string']:
                    #misspelled file name
                    pass
                else:
                   view_time_matrix.at[category, "no_text"] = row['median_system_time']
        if 'text' == row['tag_string']:
            view_time_matrix.at["Nur Text", "text"] = row['median_system_time']

    return view_time_matrix

def visualize_view_time_matrix():
    view_time_matrix = create_view_time_matrix()
    plt.figure(figsize=(10, 6))
    sns.heatmap(view_time_matrix, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Mean Viewing Time (seconds)'})
    plt.title("Viewing Time Matrix")
    plt.xlabel("Text Presence")
    plt.ylabel("Semantic Categories")
    plt.show()
visualize_view_time_matrix()

