# %%
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns


# %% [markdown]
# # Combine all CSV files into a single DataFrame

# %%
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Load all CSVs from sessions folder
directory_path = './sessions'
dataframes = []

for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory_path, filename)
        dataframes.append(pd.read_csv(file_path))

# Step 2: Combine all files
combined_df = pd.concat(dataframes, ignore_index=True)

# Step 3: Normalize and optimize club names
combined_df['Club Name'] = combined_df['Club Name'].astype(str).str.strip().str.lower()

club_name_map = {
    'driver': 'Dr', 'dr': 'Dr',
    '3 wood': '3w', '3w': '3w',
    '5 wood': '5w', '5w': '5w',
    '3 hybrid': '3h', '3h': '3h',
    '4 hybrid': '4h', '4h': '4h',
    '3 iron': '3i', '3i': '3i',
    '4 iron': '4i', '4i': '4i',
    '5 iron': '5i', '5i': '5i',
    '6 iron': '6i', '6i': '6i',
    '7 iron': '7i', '7i': '7i',
    '8 iron': '8i', '8i': '8i',
    '9 iron': '9i', '9i': '9i',
    'pitching wedge': 'PW', 'pw': 'PW',
    'gap wedge': 'GW', 'gw': 'GW',
    'sand wedge': 'SW', 'sw': 'SW',
    'lob wedge': 'LW', 'lw': 'LW',
    'wedge': 'SW', 'swedge': 'SW'  # catch-all for generic "wedge"
}
combined_df['Club Name'] = combined_df['Club Name'].map(club_name_map).fillna('Other')

# Step 4: Filter to valid club list only
valid_clubs = ['Dr', '3w', '3h', '5i', '6i', '7i', '8i', '9i', 'PW', 'GW', 'SW', 'LW']
combined_df = combined_df[combined_df['Club Name'].isin(valid_clubs)]

# Step 5: Violin plot of carry distance by club
plt.figure(figsize=(14, 6))
sns.violinplot(
    data=combined_df,
    x='Club Name',
    y='Carry (yds)',
    order=valid_clubs,
    palette='tab20',
    inner='box'
)
plt.xticks(rotation=45)
plt.title('Carry Distance Distribution by Club')
plt.tight_layout()
plt.show()
combined_df.to_csv('all_shots_gulftee.csv')


# %% [markdown]
# Filling in missing values in Club Speed (mph) and Club Speed at Impact Location (mph)

# %%
import pandas as pd
data = pd.read_csv('all_shots_gulftee.csv',index_col=0)

# %%
club_lofts = {
    'Dr': 10.5,
    '3w': 15,
    '5w': 19,
    '3h': 19,
    '4h': 22,
    '5h': 25,
    '3i': 21,
    '4i': 24,
    '5i': 27,
    '6i': 31,
    '7i': 35,
    '8i': 39,
    '9i': 43,
    'PW': 47
}

# Function to get the loft for each club
def get_club_loft(club_name):
    return club_lofts.get(club_name, None)

# Apply the function to get the loft for each club
data['Loft (deg)'] = data['Club Name'].apply(get_club_loft)


# Estimate Club Speed (mph)
def estimate_club_speed(row):
    if pd.isnull(row['Club Speed (mph)']):
        if 'Driver' in row['Club Type']:
            return row['Ball Speed (mph)'] / 1.55 # Assuming average smash factor of 1.45 for driver
        elif 'Iron' in row['Club Type']:
            return row['Ball Speed (mph)']  / 1.25
        elif 'Hybrid' in row['Club Type']:
            return row['Ball Speed (mph)'] / 1.35
        elif 'FW' in row['Club Type']:
            return row['Ball Speed (mph)'] / 1.45

    return row['Club Speed (mph)']

# Estimate Club Speed at Impact Location (mph)
def estimate_club_speed_impact(row):
    if pd.isnull(row['Club Speed at Impact Location (mph)']):
        return row['Club Speed (mph)'] * 0.98  # Assuming a slight reduction for off-center hits
    return row['Club Speed at Impact Location (mph)']

# Calculate Efficiency
def calculate_efficiency(row):
    if pd.isnull(row['Efficiency']):
        if 'Driver' in row['Club Type']:
            return row['Efficiency'] / 1.55 # Assuming average smash factor of 1.45 for driver
        elif 'Iron' in row['Club Type']:
            return row['Efficiency']  / 1.25
        elif 'Hybrid' in row['Club Type']:
            return row['Efficiency'] / 1.35
        elif 'FW' in row['Club Type']:
            return row['Efficiency'] / 1.45

    return row['Efficiency']

# Estimate Angle of Attack (deg)
#def estimate_angle_of_attack(row):
#    if pd.isnull(row['Angle of Attack (deg)']):
#        if 'Driver' in row['Club Type']:
#            return row['Launch Angle (deg)'] - 12  # Adjust to fit the +1 to +5 range
#        elif 'Iron' in row['Club Type']:
#            return row['Launch Angle (deg)'] - 5  # Adjust to fit the -3 to -6 range
#        elif 'Hybrid' in row['Club Type']:
#            return row['Launch Angle (deg)'] - 5  # Adjust to fit the -2 to +2 range
#        elif 'FW' in row['Club Type']:
#            return row['Launch Angle (deg)'] - 7  # Adjust to fit the -1 to +3 range
#    return row['Angle of Attack (deg)']

# Estimate Club Path (deg out-in-/in-out+)
def estimate_club_path(row):
    if pd.isnull(row['Club Path (deg out-in-/in-out+)']):
        return row['Push/Pull (deg L-/R+)'] * 1.2  # Assuming a relationship between path and face angle
    return row['Club Path (deg out-in-/in-out+)']

# Estimate Face to Target (deg closed-/open+)
def estimate_face_to_target(row):
    if pd.isnull(row['Face to Target (deg closed-/open+)']):
        return row['Push/Pull (deg L-/R+)']
    return row['Face to Target (deg closed-/open+)']

# Estimate Lie (deg toe down-/toe up+)
def estimate_lie(row):
    if pd.isnull(row['Lie (deg toe down-/toe up+)']):
        return 0  # Default to 0 if no data available
    return row['Lie (deg toe down-/toe up+)']

# Loft (deg) is already present in the data

# Estimate Face Impact Horizontal (mm toe-/heel+)
def estimate_face_impact_horizontal(row):
    if pd.isnull(row['Face Impact Horizontal (mm toe-/heel+)']):
        return 0  # Default if no data available
    return row['Face Impact Horizontal (mm toe-/heel+)']

# Estimate Face Impact Vertical (mm low-/high+)
def estimate_face_impact_vertical(row):
    if pd.isnull(row['Face Impact Vertical (mm low-/high+)']):
        return 0  # Default if no data available
    return row['Face Impact Vertical (mm low-/high+)']

# Estimate Closure Rate (deg/sec)
def estimate_closure_rate(row):
    if pd.isnull(row['Closure Rate (deg/sec)']):
        return 0  # Default if no data available
    return row['Closure Rate (deg/sec)']

# Apply functions to calculate missing metrics
data['Club Speed (mph)'] = data.apply(estimate_club_speed, axis=1)
data['Club Speed at Impact Location (mph)'] = data.apply(estimate_club_speed_impact, axis=1)
data['Efficiency'] = data.apply(calculate_efficiency, axis=1)
#data['Angle of Attack (deg)'] = data.apply(estimate_angle_of_attack, axis=1)
data['Club Path (deg out-in-/in-out+)'] = data.apply(estimate_club_path, axis=1)
data['Face to Target (deg closed-/open+)'] = data.apply(estimate_face_to_target, axis=1)
data['Lie (deg toe down-/toe up+)'] = data.apply(estimate_lie, axis=1)
data['Face Impact Horizontal (mm toe-/heel+)'] = data.apply(estimate_face_impact_horizontal, axis=1)
data['Face Impact Vertical (mm low-/high+)'] = data.apply(estimate_face_impact_vertical, axis=1)
data['Closure Rate (deg/sec)'] = data.apply(estimate_closure_rate, axis=1)



# %%
data['Club Name'] = data['Club Name'].replace({'5i': '5h', '4i': '4h'})

# %%
sns.boxenplot(data=data,x='Club Type',y='Side Spin (rpm L-/R+)')

# %%
import matplotlib.pyplot as plt
import seaborn as sns

# Visualize carry distance distribution
plt.figure(figsize=(10, 6))
sns.violinplot(x='Club Name', y='Carry (yds)', data=data, palette='Set1',fill=False)
sns.boxenplot(x='Club Name', y='Carry (yds)', data=data, palette='Set1', alpha=0.5, linewidth=0.5)
plt.title = 'Carry Distance Distribution by Club'
plt.xlabel('Club Name')
plt.ylabel('Carry Distance (yds)')
plt.xticks(rotation=45)
plt.show()


# %%
plt.figure(figsize=(10, 6))
sns.boxenplot(x='Club Type', y='Total Spin (rpm)', data=data, palette='Set1', hue='Club Type',legend=False)
plt.title= ('Total Spin (rpm) Distribution by Club')
plt.xlabel('Club Type')
plt.ylabel('Total Spin (rpm)')
plt.xticks(rotation=45)
plt.show()

# %%
# Visualize accuracy (Push/Pull) distribution
plt.figure(figsize=(10, 6))
sns.boxenplot(x='Club Name', y='Push/Pull (deg L-/R+)', data=data, palette="Set1")
plt.title = ('Push/Pull Distribution by Club')
plt.xlabel('Club Name')
plt.ylabel('Push/Pull (deg)')
plt.xticks(rotation=45)
plt.show()


# %%
# Visualize launch angle and Carry
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Launch Angle (deg)', y='Carry (yds)',hue = 'Club Type' ,data=data, palette='Set1')
plt.title='Launch Angle and Carry relationship'
sns.lmplot(x='Launch Angle (deg)', y='Carry (yds)', data=data, hue='Club Type', palette='Set1')
plt.xticks(rotation=45)
plt.show()


# %%
# Visualize accuracy (Push/Pull) distribution
plt.figure(figsize=(10, 6))
sns.violinplot(x='Club Name', y='Ball Speed (mph)', data=data, palette='Set1', alpha=0.5)
sns.boxenplot(x='Club Name', y='Ball Speed (mph)', data=data,  palette='Set1', fill=False)
plt.title = ('Ball Speed (mph) Distribution by Club')
plt.xlabel('Club Name')
plt.ylabel('Ball Speed (mph)')
plt.xticks(rotation=45)
plt.show()


# %%
plt.figure(figsize=(10, 6))
sns.kdeplot(x='Side Spin (rpm L-/R+)', y='Offline (yds L-/R+)', data=data,palette='Set1', hue='Club Type', alpha=0.6)
sns.scatterplot(x='Side Spin (rpm L-/R+)', y='Offline (yds L-/R+)', data=data,legend=True, hue='Club Type', palette='Set1')
plt.title('Side Spin relation to Offline')
plt.xlabel('Side Spin (rpm L-/R+)')
plt.ylabel('Offline (yds L-/R+)')
plt.xticks(rotation=45)
plt.show()


# %%
# Calculate efficiency (smash factor) summary
efficiency_summary = data.groupby('Club Name').agg({
    'Club Speed (mph)': ['mean', 'std'],
    'Ball Speed (mph)': ['mean', 'std'],
    'Carry (yds)': ['mean', 'std'],
    'Launch Angle (deg)': ['mean', 'std']

}).reset_index()

# Flatten the multi-level columns
efficiency_summary.columns = ['Club Name','Club Speed Mean', 'Club Speed Std', 
                              'Ball Speed Mean', 'Ball Speed Std', 'Carry Mean',
                              'Carry Std','Launch Angle Mean', 'Launch Angle Std']
efficiency_summary
#efficiency_summary.to_csv("Metrics/Std_Mean_by_Club.csv",index=False)


# %%
data['Spin Efficiency'] = (data['Back Spin (rpm)'] + data['Side Spin (rpm L-/R+)']) / data['Ball Speed (mph)']

# %%


# %%
data['Spin Efficiency']

# %%
# Save the updated DataFrame to a new CSV file
updated_file_path = 'updated_metrics_gulftee.csv'  # Update this path
data.to_csv(updated_file_path, index=False)
print(f"Updated CSV saved to {updated_file_path}")


