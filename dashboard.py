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
st.title(":bar_chart: North Coast Ecology Centre Interactive Dashboard")

# Reduce top padding
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# Logo 
logo_link = "https://static.wixstatic.com/media/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png/v1/fill/w_250,h_250,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png"
st.logo(logo_link, size="large", link = "https://www.northcoastecologycentresociety.com/")

st.write("When uploading files: upload square file first, then admission file second")
# File upload section
uploaded_files = st.file_uploader(":file_folder: Upload up to 2 files", type=["csv", "txt", "xlsx"], accept_multiple_files=True)

# Fallback URLs
url = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Square%20Item%20Sale%20Transactions%202023-2024%20-%20Item%20Sales.csv'
url1 = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Daily%20Admissions%20and%20Cash%20Deposits%202023%20and%202024%20-%20Original%20Values.csv'

# Initialize dataframes
df, df1 = None, None

# Handle file uploads
if uploaded_files:
    if len(uploaded_files) >= 1:
        file1 = uploaded_files[0]
        if file1.name.endswith(".csv") or file1.name.endswith(".txt"):
            df = pd.read_csv(file1, encoding="ISO-8859-1")
        elif file1.name.endswith(".xlsx"):
            df = pd.read_excel(file1)
        st.write(f"Loaded: {file1.name}")

    if len(uploaded_files) == 2:
        file2 = uploaded_files[1]
        if file2.name.endswith(".csv") or file2.name.endswith(".txt"):
            df1 = pd.read_csv(file2, encoding="ISO-8859-1")
        elif file2.name.endswith(".xlsx"):
            df1 = pd.read_excel(file2)
        st.write(f"Loaded: {file2.name}")

# Fallback to URLs if files aren't uploaded
if df is None:
    df = pd.read_csv(url, encoding="ISO-8859-1")
    st.write("Loaded: Square Item Sale Transactions 2023/2024")

if df1 is None:
    df1 = pd.read_csv(url1, encoding="ISO-8859-1")
    st.write("Loaded: Daily Admission and Cash Deposits 2023/2024")
    

# Merge datasets
df_merge = pd.concat([df, df1], ignore_index=True)

# Ensure 'Date' column exists and is in datetime format
df_merge["Date"] = pd.to_datetime(df_merge["Date"], errors='coerce')

#---Sidebar---
st.sidebar.header("Choose your filter: ")

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
hourly_fig = px.bar(hourly_counts, x='Hour Label', y='Transaction Count', title='Busiest Hours by Item Sales')
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
                     title="Busiest Days of the Week by Item Sales",
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

# Convert Date column to datetime
df1['Date'] = pd.to_datetime(df1['Date'])

# Add a new column for Day of Week
df1['Day of Week'] = df1['Date'].dt.day_name()

# Filter data based on seleted date range
df1 = df1[(df1["Date"] >= date1) & (df1["Date"] <= date2)].copy()

# Define available visitor categories (including total)
visitor_categories = ['Total Visitors', 'Cruise', 'Local', 'Northwest BC', 'Other', 'D/n pay - Family Pass']

# Let user pick a category
selected_category = st.selectbox("Select visitor category", visitor_categories)
# Group by Day of Week and sum based on selected category
visitors_by_day = df1.groupby('Day of Week')[selected_category].sum().reset_index()

# Sort days in week order
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
visitors_by_day['Day of Week'] = pd.Categorical(visitors_by_day['Day of Week'], categories=days_order, ordered=True)
visitors_by_day = visitors_by_day.sort_values('Day of Week')

# Plot
fig = px.bar(visitors_by_day,
             x='Day of Week',
             y=selected_category,
             title=f'{selected_category} by Day of the Week',
             labels={selected_category: 'Total Visitors'},
             color=selected_category)

st.plotly_chart(fig)

# --- Data Download Option ---
with st.expander("View Data of Total Visitors:"):
    st.dataframe(visitors_by_day.style.background_gradient(cmap="Greens"))
    csv = day_counts.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="TotalVisitors.csv", mime="text/csv")

# First filter the data
filtered_df = df[
    df['Category'].isin(['Gift Shop', 'None']) & 
    (df['Item'].str.lower() != 'custom amount')
].copy()

# THEN convert Qty to numeric (after filtering)
filtered_df['Qty'] = filtered_df['Qty'].astype(str)  # Ensure it's a string

def convert_qty(qty_str):
    try:
        if '+' in qty_str:
            return sum(float(x) for x in qty_str.split('+'))
        return float(qty_str)
    except:
        return 0.0  # or np.nan

filtered_df['Qty'] = filtered_df['Qty'].apply(convert_qty)  # Fix addition issue

# Group items
def group_items(name):
    name = name.lower()
    if "sticker" in name:
        return "Stickers"
    elif "zipper pull" in name:
        return "Zipper Pulls"
    elif "shirt" in name:
        return "Shirts"
    elif "stained glass" in name:
        return "Stained Glass"
    elif "magnet" in name:
        return "Magnets"
    elif "articulated sperm whale" in name:
        return "Articulated Sperm Whale"
    elif "guide pam" in name:
        return "Guide Pamphlets"
    else:
        return name.title()

# Filter
filtered_df['Grouped Item'] = filtered_df['Item'].apply(group_items)

# Sum up the quantities
item_sales = filtered_df.groupby('Grouped Item', as_index=False)['Qty'].sum()
item_sales = item_sales.sort_values('Qty', ascending=False)

# Create bar chart
fig = px.bar(item_sales,
             x='Grouped Item',
             y='Qty',
             title='Gift Shop Item Sales',
             text='Qty',
             color='Grouped Item')

# Plot bar chart
fig.update_layout(xaxis_title='Item', yaxis_title='Quantity Sold')
st.plotly_chart(fig)

# Create a pie chart
fig_pie = px.pie(
    item_sales,
    names='Grouped Item',
    values='Qty',
    title='Gift Shop Sales Distribution',
    hole=0.3,  # Optional: Makes it a donut chart (set to 0 for normal pie)
)

# Improve label readability
fig_pie.update_traces(
    textposition='inside',
    textinfo='percent+label',  # Show % and item name
    insidetextorientation='radial'  # Better for crowded pies
)

# Display the pie chart
st.plotly_chart(fig_pie)