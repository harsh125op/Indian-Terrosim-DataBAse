import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="India Terrorism Database Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)

# Add title and description
st.title("India Terrorism Database Dashboard")
st.markdown("""
This dashboard provides an interactive visualization of terrorism incidents in India.
Use the filters on the sidebar to explore specific regions, time periods, or attack types.
""")

# Load dataset
@st.cache_data
def load_data():
    file_path = "india_terrorism_database_with_summary.csv"  # Update with actual path
    # Process the date field
    df = pd.read_csv(file_path, parse_dates=['Date'])  # Ensure 'Date' is in proper datetime format
    
    # Extract Year, Month, and Month-Year
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Month-Year'] = df['Date'].dt.strftime('%Y-%m')

    return df

# Load the data
df = load_data()

# Create sidebar for filters
st.sidebar.header("Filters")

# Year range filter
year_min = int(df['Year'].min())
year_max = int(df['Year'].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

# State filter
all_states = df['State'].unique().tolist()
states_selected = st.sidebar.multiselect(
    "Select States",
    options=all_states,
    default=[]
)

# Attack type filter
all_attack_types = df['Attack Type'].unique().tolist()
attack_types_selected = st.sidebar.multiselect(
    "Select Attack Types",
    options=all_attack_types,
    default=[]
)

# Apply filters
filtered_df = df.copy()
filtered_df = filtered_df[(filtered_df['Year'] >= year_range[0]) & (filtered_df['Year'] <= year_range[1])]

if states_selected:
    filtered_df = filtered_df[filtered_df['State'].isin(states_selected)]

if attack_types_selected:
    filtered_df = filtered_df[filtered_df['Attack Type'].isin(attack_types_selected)]

# Display metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Incidents", filtered_df.shape[0])
with col2:
    st.metric("Total Casualties", filtered_df['Casualties'].sum())
with col3:
    st.metric("Avg. Casualties per Attack", round(filtered_df['Casualties'].mean(), 2))
with col4:
    if not filtered_df.empty:
        st.metric("Most Common Attack Type", filtered_df['Attack Type'].value_counts().index[0])
    else:
        st.metric("Most Common Attack Type", "N/A")

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["Temporal Analysis", "Geographical Analysis", "Attack Patterns", "Detailed Data"])

with tab1:
    st.subheader("Temporal Analysis")
    
    if not filtered_df.empty:
        monthly_data = filtered_df.groupby('Month').size().reset_index(name='Incidents')
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                        7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        monthly_data['Month_Name'] = monthly_data['Month'].map(month_names)
        monthly_data = monthly_data.sort_values('Month')
        
        fig = px.bar(monthly_data, x='Month_Name', y='Incidents', 
                    title='Monthly Distribution of Incidents',
                    labels={'Month_Name': 'Month', 'Incidents': 'Number of Incidents'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")
    
    # Heatmap of incidents by month and year
    

with tab2:
    st.subheader("Geographical Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Incidents by state
        if not filtered_df.empty:
            state_data = filtered_df.groupby('State').size().reset_index(name='Incidents')
            state_data = state_data.sort_values('Incidents', ascending=False)
            
            fig = px.bar(state_data, x='State', y='Incidents',
                        title='Number of Incidents by State',
                        color='Incidents',
                        color_continuous_scale='Viridis')
            fig.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    with col2:
        # Casualties by state
        if not filtered_df.empty:
            casualties_by_state = filtered_df.groupby('State')['Casualties'].sum().reset_index()
            casualties_by_state = casualties_by_state.sort_values('Casualties', ascending=False)
            
            fig = px.bar(casualties_by_state, x='State', y='Casualties',
                        title='Number of Casualties by State',
                        color='Casualties',
                        color_continuous_scale='Viridis')
            fig.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    

with tab3:
    st.subheader("Attack Patterns Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Attack types distribution
        if not filtered_df.empty:
            attack_type_data = filtered_df['Attack Type'].value_counts().reset_index()
            attack_type_data.columns = ['Attack Type', 'Count']
            
            fig = px.pie(attack_type_data, values='Count', names='Attack Type',
                        title='Distribution of Attack Types',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    with col2:
        # Target types distribution
        if not filtered_df.empty:
            target_type_data = filtered_df['Target Type'].value_counts().reset_index()
            target_type_data.columns = ['Target Type', 'Count']
            
            fig = px.pie(target_type_data, values='Count', names='Target Type',
                        title='Distribution of Target Types',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Perpetrators analysis
        if not filtered_df.empty:
            perp_data = filtered_df['Perpetrators'].value_counts().reset_index()
            perp_data.columns = ['Perpetrator Group', 'Incidents']
            perp_data = perp_data.sort_values('Incidents', ascending=False).head(10)
            
            fig = px.bar(perp_data, x='Perpetrator Group', y='Incidents',
                        title='Top Perpetrator Groups by Number of Incidents',
                        color='Incidents',
                        color_continuous_scale='Reds')
            fig.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    with col2:
        # Weapons analysis
        if not filtered_df.empty:
            weapon_data = filtered_df['Weapons Used'].value_counts().reset_index()
            weapon_data.columns = ['Weapon Type', 'Frequency']
            
            fig = px.bar(weapon_data, x='Weapon Type', y='Frequency',
                        title='Distribution of Weapons Used',
                        color='Frequency',
                        color_continuous_scale='Blues')
            fig.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    
    # Correlation between attack types and casualties
    if not filtered_df.empty:
        attack_casualties = filtered_df.groupby('Attack Type')['Casualties'].agg(['mean', 'sum', 'count']).reset_index()
        attack_casualties = attack_casualties.sort_values('sum', ascending=False)
        
        fig = px.bar(attack_casualties, x='Attack Type', y=['mean', 'sum'],
                    barmode='group',
                    title='Casualties by Attack Type',
                    labels={'value': 'Casualties', 'variable': 'Metric'},
                    color_discrete_sequence=['#ff7f0e', '#1f77b4'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with tab4:
    st.subheader("Detailed Data Analysis")
    
    # Add incident count over time (interactive)
    if not filtered_df.empty:
        incidents_over_time = filtered_df.groupby('Month-Year').size().reset_index(name='Incidents')
        incidents_over_time['Month-Year'] = pd.to_datetime(incidents_over_time['Month-Year'])
        incidents_over_time = incidents_over_time.sort_values('Month-Year')
        
        fig = px.line(incidents_over_time, x='Month-Year', y='Incidents',
                     title='Incidents Over Time',
                     labels={'Month-Year': 'Date', 'Incidents': 'Number of Incidents'})
        fig.update_xaxes(rangeslider_visible=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")
    
    # Display data table with option to download
    st.subheader("Raw Data Table")
    if not filtered_df.empty:
        display_cols = ['Date', 'State', 'City', 'Attack Type', 'Target Type', 'Casualties', 'Perpetrators', 'Weapons Used', 'Sources']
        st.dataframe(filtered_df[display_cols], hide_index=True)
        
        # Add download button
        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        
        csv = convert_df_to_csv(filtered_df)
        st.download_button(
            "Download Filtered Data as CSV",
            csv,
            "india_terrorism_filtered_data.csv",
            "text/csv",
            key='download-csv'
        )
        
        # Display additional insights
        st.subheader("Data Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Most deadly attacks
            deadliest = filtered_df.sort_values('Casualties', ascending=False).head(5)
            st.write("Top 5 Deadliest Attacks:")
            for i, row in deadliest.iterrows():
                st.markdown(f"**{row['Date'].strftime('%d %b %Y')}**: {row['City']}, {row['State']} - {row['Casualties']} casualties ({row['Attack Type']} by {row['Perpetrators']})")
                st.markdown(f"[Source]({row['Sources']})")
        
        with col2:
            # Most active regions
            active_cities = filtered_df.groupby('City').size().sort_values(ascending=False).head(5)
            st.write("Most Active Cities:")
            for city, count in active_cities.items():
                st.markdown(f"**{city}**: {count} incidents")
            
            # Show summary examples
            st.write("Recent Attack Summaries:")
            recent = filtered_df.sort_values('Date', ascending=False).head(3)
            for i, row in recent.iterrows():
                st.markdown(f"**{row['Date'].strftime('%d %b %Y')}**: {row['Summary']}")
    else:
        st.info("No data available for the selected filters.")

# Add footer
st.markdown("---")
st.markdown("**India Terrorism Database Dashboard** • Created with Streamlit")
st.markdown("Data visualization and analysis tool for tracking terrorism incidents in India")

# Add instructions for using real data
with st.expander("How to Use With Your Data"):
    st.markdown("""
    ### Using Your Own Data
    
    To use this dashboard with your own data, follow these steps:
    
    1. Prepare your JSON data file with the following fields:
       - Date (in the format shown in the example)
       - State
       - City
       - Attack Type
       - Target Type
       - Casualties
       - Perpetrators
       - Weapons Used
       - Sources
       - Summary
    
    2. Replace the `load_data()` function with:
    
    ```python
    @st.cache_data
    def load_data():
        # Load the JSON data
        with open('your_data.json', 'r') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Process the date field
        df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x['$date'].split('T')[0], '%Y-%m-%d'))
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Month-Year'] = df['Date'].dt.strftime('%Y-%m')
        
        return df
    ```
    
    3. Run the Streamlit app with:
    
    ```
    streamlit run app.py
    ```
    """)