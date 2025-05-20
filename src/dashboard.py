import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
all_shots_df = pd.read_csv('data/formatted_all_rounds_data.csv', parse_dates=['Date'])

# Set up the Streamlit app
st.title('Golf Performance Dashboard')

# Sidebar Filters
st.sidebar.header('Filter Data')

# Date Range Filter
start_date = st.sidebar.date_input('Start Date', all_shots_df['Date'].min())
end_date = st.sidebar.date_input('End Date', all_shots_df['Date'].max())

# Club Selection
clubs = all_shots_df['Club'].unique()
selected_clubs = st.sidebar.multiselect('Select Clubs', clubs, default=clubs)

# Filter the data based on selections
mask = (all_shots_df['Date'] >= pd.to_datetime(start_date)) & (all_shots_df['Date'] <= pd.to_datetime(end_date))
mask &= all_shots_df['Club'].isin(selected_clubs)
filtered_data = all_shots_df[mask]

# Display filtered data
st.header('Filtered Shot Data')
st.dataframe(filtered_data)

# Key Metrics
st.header('Key Performance Metrics')

avg_carry = filtered_data['Carry (yds)'].mean()
avg_total_distance = filtered_data['Total Distance (yds)'].mean()
avg_ball_speed = filtered_data['Ball Speed'].mean()

col1, col2, col3 = st.columns(3)
col1.metric('Average Carry Distance (yds)', f"{avg_carry:.1f}")
col2.metric('Average Total Distance (yds)', f"{avg_total_distance:.1f}")
col3.metric('Average Ball Speed (mph)', f"{avg_ball_speed:.1f}")

# Visualization
st.header('Carry Distance Distribution')
fig, ax = plt.subplots()
filtered_data['Carry (yds)'].hist(bins=30, ax=ax)
st.pyplot(fig)

# Scatter Plot of Carry vs. Ball Speed
st.header('Carry Distance vs. Ball Speed')
fig2, ax2 = plt.subplots()
ax2.scatter(filtered_data['Ball Speed'], filtered_data['Carry (yds)'])
ax2.set_xlabel('Ball Speed (mph)')
ax2.set_ylabel('Carry Distance (yds)')
st.pyplot(fig2)
