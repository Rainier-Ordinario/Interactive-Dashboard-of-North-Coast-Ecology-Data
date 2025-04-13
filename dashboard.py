# Interactive Dashboard for North Coast Ecology Centre
# Author: Rainier Ordinario
# Date: April 12, 2025

import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib as plt                      
import os
import warnings
warnings.filterwarnings('ignore')

# Set layout for page
st.set_page_config(page_title="NCEC EDA", page_icon=":bar_chart:",layout="wide")

# Set title and format
st.title(" :bar_chart: North Coast Ecology Centre Dashboard of 2023/2024 Data ")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# Use raw file
url = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Square%20Item%20Sale%20Transactions%202023-2024%20-%20Item%20Sales.csv'
df = pd.read_csv(url, encoding="ISO-8859-1")

# Allow users to select a date
col1, col2 = st.columns((2))
df["Date"] = pd.to_datetime(df["Date"])

# Get the minimum and maximum date
startDate = pd.to_datetime(df["Date"]).min()
endDate = pd.to_datetime(df["Date"]).max()

# Allow user to select a time frame 
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter data based on seleted date range
df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

# # Filter data based on category (Admission, Donations, Gift Shop)
# st.sidebar.header("Choose your filter: ")
# category = st.sidebar.multiselect("Pick your Region", df["Category"].unique())

# # Allow user to not select any category
# if not category:
#     df2 = df.copy()
# else:
#     df2 = df[df["Category"].isin(category)]

# Category seel
# 1. Get unique categories + "All"
categories = df['Category'].dropna().unique().tolist()
categories.sort()
categories.insert(0, "All")  # Insert "All" at the top

# 2. Category selector
selected_category = st.selectbox("Select a category", categories)

# 3. Apply filter
if selected_category != "All":
    filtered_df = df[df['Category'] == selected_category]
else:
    filtered_df = df.copy()



# Convert Time column to datetime if not already
filtered_df['Time'] = filtered_df['Time'].str.replace(r':(am|pm)', r' \1', case=False, regex=True)

# Count number of transactions per hour
filtered_df['Hour'] = pd.to_datetime(filtered_df['Time'], format='%I:%M %p').dt.hour

#Hour counts
hourly_counts = filtered_df.groupby('Hour').size().reset_index(name='Transaction Count')

#Plot
fig = px.bar(hourly_counts, x='Hour', y='Transaction Count', title='Busiest Hours')
st.plotly_chart(fig)

