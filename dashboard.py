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
st.title(":bar_chart: North Coast Ecology Centre Dashboard")

# Reduce top padding
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# Logo attempt
# logo_link = "https://static.wixstatic.com/media/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png/v1/fill/w_250,h_250,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png"
# st.logo(logo_link, link = "https://static.wixstatic.com/media/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png/v1/fill/w_250,h_250,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png")


# Use raw files
url = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Square%20Item%20Sale%20Transactions%202023-2024%20-%20Item%20Sales.csv'
url1 = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Daily%20Admissions%20and%20Cash%20Deposits%202023%20and%202024%20-%20Original%20Values.csv'

df = pd.read_csv(url, encoding="ISO-8859-1")
df1 = pd.read_csv(url1, encoding="ISO-8859-1")

# Merge datasets
df_merge = pd.concat([df, df1], ignore_index=True)

# Ensure 'Date' column exists and is in datetime format
df_merge["Date"] = pd.to_datetime(df_merge["Date"], errors='coerce')

# Allow users to select a date
col1, col2 = st.sidebar.columns((2))
df["Date"] = pd.to_datetime(df["Date"])

# Set initial values
startDate = pd.to_datetime("2023-01-01").date()
endDate = pd.to_datetime("2024-12-31").date()


col_buttons = st.sidebar.columns(3)

if col_buttons[0].button("2023"):
    startDate = pd.to_datetime("2023-01-01").date()
    endDate = pd.to_datetime("2023-12-31").date()

if col_buttons[1].button("2024"):
    startDate = pd.Timestamp("2024-01-01").date()
    endDate = pd.Timestamp("2024-12-31").date()

if col_buttons[2].button("23/24"):
    startDate = pd.Timestamp("2023-01-01").date()
    endDate = pd.Timestamp("2024-12-31").date()

# Allow user to select a time frame 
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
   
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter data based on seleted date range
df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

# 1. Get unique categories + "All"
categories = df['Category'].dropna().unique().tolist()
categories.sort()
categories.insert(0, "All")  # Insert "All" at the top

# 2. Category selector
selected_category = st.sidebar.selectbox("Select a category", categories)

# 3. Apply filter
if selected_category != "All":
    filtered_df = df[df['Category'] == selected_category]
else:
    filtered_df = df.copy()

#TIME COLUMN
# Convert Time column to datetime if not already
filtered_df['Time'] = filtered_df['Time'].str.replace(r':(am|pm)', r' \1', case=False, regex=True)
filtered_df['Time'] = pd.to_datetime(filtered_df['Time'], format='%I:%M %p')

# Extract hour and format for label
filtered_df['Hour'] = filtered_df['Time'].dt.hour
filtered_df['Hour Label'] = filtered_df['Time'].dt.strftime('%I:00 %p')  # e.g., 01:00 PM

# Group by hour and get counts
hourly_counts = filtered_df.groupby(['Hour', 'Hour Label']).size().reset_index(name='Transaction Count')

# Sort by actual hour
hourly_counts = hourly_counts.sort_values('Hour')

# Plot using formatted labels
hourly_fig = px.bar(hourly_counts, x='Hour Label', y='Transaction Count', title='Busiest Hours')
st.plotly_chart(hourly_fig)

# Allow user to download hourly counts data
with st.expander("View Data of Hourly Counts:"):
    st.write(hourly_counts[['Hour Label', 'Transaction Count']].style.background_gradient(cmap="Blues"))
    csv = hourly_counts[['Hour Label', 'Transaction Count']].to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="HourlyCounts.csv", mime='text/csv')

# --- Apply Filters ---
# Filter by date range
# Filter data based on the selected date range by converting the selected dates to Pandas Timestamps
filtered_df = df[(df["Date"] >= pd.Timestamp(startDate)) & 
                 (df["Date"] <= pd.Timestamp(endDate))].copy()

# Filter by category if not "All"
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# --- Aggregate Data: Busiest Days ---
# Extract day of the week from the Date.
filtered_df["Day"] = filtered_df["Date"].dt.day_name()

# Count transactions per weekday.
day_counts = filtered_df["Day"].value_counts().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
).reset_index()
day_counts.columns = ["Day", "Transaction Count"]

# --- Visualization ---
if not day_counts.empty:
    day_fig = px.bar(day_counts,
                     x="Day",
                     y="Transaction Count",
                     title="Busiest Days of the Week",
                     labels={"Day": "Day of the Week", "Transaction Count": "Number of Transactions"})
    st.plotly_chart(day_fig)
else:
    st.write("No data available for the selected filters.")

# --- Data Download Option ---
with st.expander("View Data of Daily Counts:"):
    st.dataframe(day_counts.style.background_gradient(cmap="Greens"))
    csv = day_counts.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="BusiestDays.csv", mime="text/csv")

#----------------------------------------------------------------
# Use Brandie's Values

