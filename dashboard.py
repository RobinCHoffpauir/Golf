import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Golf Performance Analytics",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E8B57;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_session_data():
    """Load and combine all CSV files from the sessions folder"""
    sessions_dir = './sessions'
    dataframes = []
    
    if not os.path.exists(sessions_dir):
        st.error(f"Sessions directory '{sessions_dir}' not found!")
        return pd.DataFrame()
    
    csv_files = [f for f in os.listdir(sessions_dir) if f.endswith('.csv')]
    
    if not csv_files:
        st.error("No CSV files found in sessions directory!")
        return pd.DataFrame()
    
    for filename in csv_files:
        try:
            file_path = os.path.join(sessions_dir, filename)
            df = pd.read_csv(file_path)
            df['Session_File'] = filename
            dataframes.append(df)
        except Exception as e:
            st.warning(f"Could not load {filename}: {str(e)}")
    
    if not dataframes:
        return pd.DataFrame()
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    return clean_and_process_data(combined_df)

def clean_and_process_data(df):
    """Clean and process the combined golf data"""
    if df.empty:
        return df
    
    # Normalize club names
    df['Club Name'] = df['Club Name'].astype(str).str.strip().str.lower()
    
    club_name_map = {
        'driver': 'Dr', 'dr': 'Dr',
        '3 wood': '3w', '3w': '3w', 'fw': '3w',
        '5 wood': '5w', '5w': '5w',
        '3 hybrid': '3h', '3h': '3h',
        '4 hybrid': '4h', '4h': '4h',
        '5 hybrid': '5h', '5h': '5h',
        '3 iron': '3i', '3i': '3i',
        '4 iron': '4i', '4i': '4i',
        '5 iron': '5i', '5i': '5i', '5 iron5i': '5i',
        '6 iron': '6i', '6i': '6i',
        '7 iron': '7i', '7i': '7i',
        '8 iron': '8i', '8i': '8i', '8 iron': '8i',
        '9 iron': '9i', '9i': '9i', '9 iron': '9i',
        'pitching wedge': 'PW', 'pw': 'PW',
        'gap wedge': 'GW', 'gw': 'GW', 'gap wdge': 'GW',
        'sand wedge': 'SW', 'sw': 'SW',
        'lob wedge': 'LW', 'lw': 'LW',
        'wedge': 'SW'
    }
    
    df['Club Name'] = df['Club Name'].map(club_name_map).fillna(df['Club Name'])
    
    # Convert date column
    if 'Shot Created Date' in df.columns:
        df['Shot Created Date'] = pd.to_datetime(df['Shot Created Date'], errors='coerce')
        df['Date'] = df['Shot Created Date'].dt.date
    
    # Ensure numeric columns
    numeric_cols = [
        'Ball Speed (mph)', 'Push/Pull (deg L-/R+)', 'Launch Angle (deg)',
        'Back Spin (rpm)', 'Side Spin (rpm L-/R+)', 'Total Spin (rpm)',
        'Carry (yds)', 'Total Distance (yds)', 'Offline (yds L-/R+)',
        'Peak Height (yds)', 'Descent Angle (deg)'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter to valid clubs
    valid_clubs = ['Dr', '3w', '5w', '3h', '4h', '5h', '3i', '4i', '5i', '6i', '7i', '8i', '9i', 'PW', 'GW', 'SW', 'LW']
    df = df[df['Club Name'].isin(valid_clubs)]
    
    # Remove rows with missing critical data
    df = df.dropna(subset=['Ball Speed (mph)', 'Carry (yds)'])
    
    return df

def create_performance_metrics(df):
    """Calculate key performance metrics"""
    if df.empty:
        return {}
    
    metrics = {
        'total_shots': len(df),
        'avg_carry': df['Carry (yds)'].mean(),
        'avg_ball_speed': df['Ball Speed (mph)'].mean(),
        'avg_launch_angle': df['Launch Angle (deg)'].mean(),
        'sessions_count': df['Session_File'].nunique() if 'Session_File' in df.columns else 0,
        'clubs_used': df['Club Name'].nunique(),
        'date_range': (df['Date'].min(), df['Date'].max()) if 'Date' in df.columns else (None, None)
    }
    return metrics

def main():
    # Header
    st.markdown('<h1 class="main-header">⛳ Golf Performance Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading golf data..."):
        df = load_all_session_data()
    
    if df.empty:
        st.error("No data available. Please check your sessions folder and CSV files.")
        return
    
    # Sidebar filters
    st.sidebar.header("📊 Data Filters")
    
    # Date range filter
    if 'Date' in df.columns and not df['Date'].isna().all():
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(df['Date'].min(), df['Date'].max()),
            min_value=df['Date'].min(),
            max_value=df['Date'].max()
        )
        
        if len(date_range) == 2:
            df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]
    
    # Club selection
    available_clubs = sorted(df['Club Name'].unique())
    selected_clubs = st.sidebar.multiselect(
        "Select Clubs",
        available_clubs,
        default=available_clubs
    )
    
    if selected_clubs:
        df = df[df['Club Name'].isin(selected_clubs)]
    
    # Ball speed range
    if 'Ball Speed (mph)' in df.columns:
        speed_range = st.sidebar.slider(
            "Ball Speed Range (mph)",
            min_value=int(df['Ball Speed (mph)'].min()),
            max_value=int(df['Ball Speed (mph)'].max()),
            value=(int(df['Ball Speed (mph)'].min()), int(df['Ball Speed (mph)'].max()))
        )
        df = df[(df['Ball Speed (mph)'] >= speed_range[0]) & (df['Ball Speed (mph)'] <= speed_range[1])]
    
    # Performance metrics
    metrics = create_performance_metrics(df)
    
    # Display key metrics
    st.subheader("📈 Key Performance Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Shots", f"{metrics['total_shots']:,}")
    with col2:
        st.metric("Avg Carry Distance", f"{metrics['avg_carry']:.1f} yds")
    with col3:
        st.metric("Avg Ball Speed", f"{metrics['avg_ball_speed']:.1f} mph")
    with col4:
        st.metric("Avg Launch Angle", f"{metrics['avg_launch_angle']:.1f}°")
    with col5:
        st.metric("Sessions Analyzed", metrics['sessions_count'])
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "🎯 Distance Analysis", "📐 Launch Conditions", 
        "🌪️ Spin Analysis", "📋 Detailed Data"
    ])
    
    with tab1:
        st.subheader("Performance Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Carry distance by club
            fig = px.box(
                df, x='Club Name', y='Carry (yds)',
                title="Carry Distance Distribution by Club",
                color='Club Name'
            )
            fig.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Ball speed by club
            fig = px.violin(
                df, x='Club Name', y='Ball Speed (mph)',
                title="Ball Speed Distribution by Club",
                color='Club Name'
            )
            fig.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Club usage frequency
        club_counts = df['Club Name'].value_counts()
        fig = px.bar(
            x=club_counts.index, y=club_counts.values,
            title="Shot Frequency by Club",
            labels={'x': 'Club', 'y': 'Number of Shots'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Distance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Carry vs Total Distance
            fig = px.scatter(
                df, x='Carry (yds)', y='Total Distance (yds)',
                color='Club Name', title="Carry vs Total Distance",
                hover_data=['Launch Angle (deg)', 'Ball Speed (mph)']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distance efficiency by club
            if 'Total Distance (yds)' in df.columns and 'Carry (yds)' in df.columns:
                df['Roll'] = df['Total Distance (yds)'] - df['Carry (yds)']
                avg_roll = df.groupby('Club Name')['Roll'].mean().reset_index()
                
                fig = px.bar(
                    avg_roll, x='Club Name', y='Roll',
                    title="Average Roll Distance by Club",
                    color='Roll', color_continuous_scale='viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Distance trends over time
        if 'Date' in df.columns:
            daily_avg = df.groupby(['Date', 'Club Name'])['Carry (yds)'].mean().reset_index()
            fig = px.line(
                daily_avg, x='Date', y='Carry (yds)', color='Club Name',
                title="Carry Distance Trends Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Launch Conditions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Launch angle vs carry
            fig = px.scatter(
                df, x='Launch Angle (deg)', y='Carry (yds)',
                color='Club Name', title="Launch Angle vs Carry Distance",
                trendline="ols"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Ball speed vs carry
            fig = px.scatter(
                df, x='Ball Speed (mph)', y='Carry (yds)',
                color='Club Name', title="Ball Speed vs Carry Distance",
                trendline="ols"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Launch angle distribution
        fig = px.histogram(
            df, x='Launch Angle (deg)', color='Club Name',
            title="Launch Angle Distribution", nbins=30,
            marginal="box"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Spin Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Total spin by club
            fig = px.box(
                df, x='Club Name', y='Total Spin (rpm)',
                title="Total Spin Distribution by Club",
                color='Club Name'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Side spin vs offline
            if 'Side Spin (rpm L-/R+)' in df.columns and 'Offline (yds L-/R+)' in df.columns:
                fig = px.scatter(
                    df, x='Side Spin (rpm L-/R+)', y='Offline (yds L-/R+)',
                    color='Club Name', title="Side Spin vs Offline Distance",
                    trendline="ols"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Spin efficiency analysis
        if 'Back Spin (rpm)' in df.columns and 'Side Spin (rpm L-/R+)' in df.columns:
            df['Spin_Efficiency'] = df['Back Spin (rpm)'] / (df['Back Spin (rpm)'] + abs(df['Side Spin (rpm L-/R+)']))
            
            fig = px.box(
                df, x='Club Name', y='Spin_Efficiency',
                title="Spin Efficiency by Club (Back Spin / Total Spin)",
                color='Club Name'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("Detailed Data Analysis")
        
        # Club performance summary
        st.subheader("Club Performance Summary")
        
        summary_stats = df.groupby('Club Name').agg({
            'Ball Speed (mph)': ['mean', 'std', 'count'],
            'Carry (yds)': ['mean', 'std', 'min', 'max'],
            'Launch Angle (deg)': ['mean', 'std'],
            'Total Spin (rpm)': ['mean', 'std']
        }).round(2)
        
        # Flatten column names
        summary_stats.columns = [f"{col[0]}_{col[1]}" for col in summary_stats.columns]
        summary_stats = summary_stats.reset_index()
        
        st.dataframe(summary_stats, use_container_width=True)
        
        # Raw data with filters
        st.subheader("Raw Shot Data")
        
        # Additional filters for detailed view
        col1, col2 = st.columns(2)
        with col1:
            show_columns = st.multiselect(
                "Select columns to display",
                df.columns.tolist(),
                default=['Club Name', 'Ball Speed (mph)', 'Carry (yds)', 
                        'Launch Angle (deg)', 'Total Spin (rpm)', 'Date']
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ['Shot Created Date', 'Carry (yds)', 'Ball Speed (mph)', 'Club Name'],
                index=0
            )
        
        if show_columns:
            display_df = df[show_columns].sort_values(sort_by, ascending=False)
            st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download processed data
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Processed Data as CSV",
            data=csv,
            file_name=f"golf_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Sidebar information
with st.sidebar:
    st.markdown("---")
    st.subheader("📋 Dashboard Info")
    st.info("""
    This dashboard analyzes your golf performance data from launch monitor sessions.
    
    **Features:**
    - Performance metrics overview
    - Distance analysis and trends
    - Launch condition optimization
    - Spin rate analysis
    - Detailed data exploration
    
    **Data Sources:**
    - Session CSV files from /sessions folder
    - Automated data cleaning and normalization
    """)
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()