import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Set auto-refresh interval (in seconds)
st_autorefresh(interval=1800000)  # 30 minutes = 1800000 milliseconds

# Function to scrape total ads from the site
def fetch_total_ads():
    url = 'https://ikman.lk/en/ads/sri-lanka/cars'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        total_ads_element = soup.find('span', class_='ads-count-text--1UYy_')
        
        if total_ads_element:
            total_ads_text = total_ads_element.text.strip()
            ads_count_match = re.search(r'of ([\d,]+) ads', total_ads_text)
            
            if ads_count_match:
                total_ads = int(ads_count_match.group(1).replace(',', ''))
                return total_ads
    return None

# Create or load a DataFrame to store the data
if 'ads_data' not in st.session_state:
    st.session_state.ads_data = pd.DataFrame(columns=['Time', 'Total Ads'])

# Function to fetch data and update the DataFrame every 30 minutes
def update_data():
    total_ads = fetch_total_ads()
    if total_ads is not None:
        # Get current time and create a new row with data
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_data = pd.DataFrame({'Time': [current_time], 'Total Ads': [total_ads]})
        
        # Use pd.concat() to add the new row to the DataFrame
        st.session_state.ads_data = pd.concat([st.session_state.ads_data, new_data], ignore_index=True)
        
        # Convert 'Time' column to datetime type for plotting
        st.session_state.ads_data['Time'] = pd.to_datetime(st.session_state.ads_data['Time'])
    else:
        st.error("Failed to fetch the ads count!")

# Streamlit app
st.title("Ikman.lk Car Ads Count Over Time")

# Fetch data if app is refreshed and more than 30 minutes have passed
if 'last_update' not in st.session_state or (datetime.now() - st.session_state.last_update).total_seconds() > 1800:
    update_data()
    st.session_state.last_update = datetime.now()

# Plot the data if it exists
if not st.session_state.ads_data.empty:
    fig = px.line(st.session_state.ads_data, x='Time', y='Total Ads', title='Total Ads Over Time')
    st.plotly_chart(fig)

    # Add a button to download the dataset as CSV
    csv = st.session_state.ads_data.to_csv(index=False).encode('utf-8')  # Convert DataFrame to CSV
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='ads_data.csv',
        mime='text/csv',
    )

# Optionally, display the raw data
if st.checkbox('Show raw data'):
    st.write(st.session_state.ads_data)
