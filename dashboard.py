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

"""
Side Bar
"""

# Allow users to select a date
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Get the minimum and maximum date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

# Allow user to select a time frame 
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter data based on seleted date range
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Filter data based on region
st.sidebar.header("Choose your filter: ")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
