# Interactive Dashboard for North Coast Ecology Centre
# Author: Rainier Ordinario
# Date: May 1, 2025

import streamlit as st
import plotly.express as px  
import pandas as pd 
import warnings
warnings.filterwarnings('ignore')

# Set layout for page
st.set_page_config(page_title="NCEC EDA", page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: North Coast Ecology Centre Interactive Dashboard")

# Reduce top padding
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# Logo
logo_link = "https://static.wixstatic.com/media/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png/v1/fill/w_250,h_250,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/abc0c5_178bdd479f554ac799217ff7b61e3892~mv2.png"

st.sidebar.markdown(
    f"""
    <div style="margin-top: -70px; margin-bottom: 20px; margin-left: 30px;">
        <a href="https://www.northcoastecologycentresociety.com/" target="_blank">
            <img src="{logo_link}" width="180" />
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("Upload Square data first, then Admissions data. If no files are uploaded, default data will be used.")

# File upload section
uploaded_files = st.file_uploader(":file_folder: Upload up to 2 files", type=["csv", "txt", "xlsx"], accept_multiple_files=True)

# Initialize URLs - now loading all years by default
# Square Transaction Files
url_2023_2024 = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Square%20Item%20Sale%20Transactions%202023-2024%20-%20Item%20Sales.csv'
url_2025 = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Square%20Item%20Sale%20Transactions%202025.csv'

# Daily Admissions and Cash Deposit Files
url1_2023_2024 = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Daily%20Admissions%20and%20Cash%20Deposits%202023%20and%202024%20-%20Original%20Values.csv'
url1_2025 = 'https://raw.githubusercontent.com/Rainier-Ordinario/Interactive-Dashboard-of-North-Coast-Ecology-Data/refs/heads/main/Daily%20Admissions%202025.csv'

# Load all default data from URLs
df_2023_2024 = pd.read_csv(url_2023_2024, encoding="ISO-8859-1")
df_2025 = pd.read_csv(url_2025, encoding="ISO-8859-1")
df = pd.concat([df_2023_2024, df_2025], ignore_index=True)

df1_2023_2024 = pd.read_csv(url1_2023_2024, encoding="ISO-8859-1")
df1_2025 = pd.read_csv(url1_2025, encoding="ISO-8859-1")
df1 = pd.concat([df1_2023_2024, df1_2025], ignore_index=True)

# Handle file uploads - append to existing data (if they want to add even more data)
if uploaded_files:
    if len(uploaded_files) >= 1:
        file1 = uploaded_files[0]
        if file1.name.endswith(".csv") or file1.name.endswith(".txt"):
            df_new = pd.read_csv(file1, encoding="ISO-8859-1")
        elif file1.name.endswith(".xlsx"):
            df_new = pd.read_excel(file1)
        
        df = pd.concat([df, df_new], ignore_index=True)

    if len(uploaded_files) == 2:
        file2 = uploaded_files[1]
        if file2.name.endswith(".csv") or file2.name.endswith(".txt"):
            df1_new = pd.read_csv(file2, encoding="ISO-8859-1")
        elif file2.name.endswith(".xlsx"):
            df1_new = pd.read_excel(file2)
        
        df1 = pd.concat([df1, df1_new], ignore_index=True)
    
# Add custom CSS to set different background colors
st.markdown("""
    <style>
        /* Top section background */
        .top-section {
            background-color: #e0f7fa;
            padding: 28px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        /* Bottom section background */
        .bottom-section {
            background-color: #fbe9e7;
            padding: 30px;
            border-radius: 10px;
        }

        .top-text {
            font-size: 30px;
            font-weight: bold;
            color: #006064;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Square Transactions Data Label
st.markdown("""
    <div class="top-section">
        <div class="top-text">Square Transactions Data</div>
    </div>
""", unsafe_allow_html=True)

# Merge datasets
df_merge = pd.concat([df, df1], ignore_index=True)

# Ensure 'Date' column exists and is in datetime format
df_merge["Date"] = pd.to_datetime(df_merge["Date"], errors='coerce')

# Sidebar time filter
st.sidebar.header("Choose your filter: ")

# Allow users to select a date
col1, col2 = st.sidebar.columns((2))
df["Date"] = pd.to_datetime(df["Date"])

# ---- Year buttons based ONLY on uploaded dataset ----
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

available_years = sorted(
    df["Date"].dt.year.dropna().unique().astype(int)
)

# Default range = full dataset
startDate = pd.Timestamp(f"{available_years[0]}-01-01").date()
endDate = pd.Timestamp(f"{available_years[-1]}-12-31").date()

col_buttons = st.sidebar.columns(len(available_years) + 1)

for i, year in enumerate(available_years):
    if col_buttons[i].button(str(year)):
        startDate = pd.Timestamp(f"{year}-01-01").date()
        endDate = pd.Timestamp(f"{year}-12-31").date()

if col_buttons[-1].button("All"):
    startDate = pd.Timestamp(f"{available_years[0]}-01-01").date()
    endDate = pd.Timestamp(f"{available_years[-1]}-12-31").date()


# Allow user to select a time frame 
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
   
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter data based on seleted date range
df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

# Get unique categories + "All"
categories = df['Category'].dropna().unique().tolist()
categories.sort()
categories.insert(0, "All")  # Insert "All" at the top

# Category selector
selected_category = st.selectbox("Select a category", categories)

# Apply filter
if selected_category != "All":
    filtered_df = df[df['Category'] == selected_category]
else:
    filtered_df = df.copy()

# Convert Time column to datetime (handles 12h, 24h, and mixed formats)
def parse_time_flexible(time_str):
    if pd.isna(time_str):
        return pd.NaT
    
    time_str = str(time_str).strip()
    
    # Try 12-hour format first (e.g., "9:50:pm" or "9:50 PM")
    try:
        return pd.to_datetime(time_str, format='%I:%M:%p')
    except:
        pass
    
    try:
        return pd.to_datetime(time_str, format='%I:%M %p')
    except:
        pass
    
    # Try 24-hour format (e.g., "16:44:25")
    try:
        return pd.to_datetime(time_str, format='%H:%M:%S')
    except:
        pass
    
    try:
        return pd.to_datetime(time_str, format='%H:%M')
    except:
        pass
    
    # Last resort: let pandas figure it out
    try:
        return pd.to_datetime(time_str)
    except:
        return pd.NaT

filtered_df['Time'] = filtered_df['Time'].apply(parse_time_flexible)

# Extract hour
filtered_df['Hour'] = filtered_df['Time'].dt.hour

# Create formatted hour labels (01:00 PM, etc.)
filtered_df['Hour Label'] = filtered_df['Time'].dt.strftime('%I:00 %p')

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

# Filter data based on the selected date range by converting the selected dates to Pandas Timestamps
df_filtered_by_date = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()


# Filter by category if not "All"
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

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

# Download data option
with st.expander("View Data of Daily Counts:"):
    st.dataframe(day_counts.style.background_gradient(cmap="Greens"))
    csv = day_counts.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="BusiestDays.csv", mime="text/csv")

# Create graph for money vs time
# Let user choose grouping: Monthly or Yearly
group_option = st.selectbox("Group by", ["Monthly", "Yearly"])

if group_option == "Monthly":
    filtered_df['Period'] = filtered_df['Date'].dt.to_period('M').astype(str)
    title = "Net Sales by Month Based on Item Sales (Square Transactions)"
elif group_option == "Yearly":
    filtered_df['Period'] = filtered_df['Date'].dt.year.astype(str)
    title = "Net Sales by Year Based on Item Sales (Square Transactions)"


# Clean 'Net Sales' column (remove $ and commas) and convert to float
filtered_df['Net Sales'] = filtered_df['Net Sales'].replace('[\\$,]', '', regex=True).astype(float)

# Group and sum net sales
sales_by_period = filtered_df.groupby('Period')['Net Sales'].sum().reset_index()

# Plot bar chart
fig = px.bar(
    sales_by_period,
    x='Period',
    y='Net Sales',
    title=title,
    labels={'Period': 'Time Period', 'Net Sales': 'Net Sales ($)'},
    color='Net Sales',
    text_auto='.2s'
)

fig.update_layout(
    xaxis_title='Period',
    yaxis_title='Net Sales ($)',
    xaxis_tickangle=-45
)

st.plotly_chart(fig)

# Ensure 'Payment Method' column exists
if 'Payment Method' in df.columns:
    # Count each payment method
    payment_counts = df['Payment Method'].value_counts().reset_index()
    payment_counts.columns = ['Payment Method', 'Count']

    # Create a pie chart
    fig = px.pie(payment_counts, 
                 names='Payment Method', 
                 values='Count',
                 title='Payment Method Distribution',
                 color_discrete_sequence=px.colors.sequential.RdBu)

    st.plotly_chart(fig)
else:
    st.warning("Payment Method column not found in the dataset.")

# First filter the data
filtered_df = df[
    df['Category'].isin(['Gift Shop', 'None']) & 
    (df['Item'].str.lower() != 'custom amount')
].copy()

# Then convert Qty to numeric (after filtering)
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

# Plot pie chart
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

'''
---------------------------------------------------------------------------------------------------
'''
# Add custom CSS to set different background colors
st.markdown("""
    <style>
        /* Top section background */
        .top-section {
            background-color: #e0f7fa;
            padding: 28px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        /* Bottom section background */
        .bottom-section {
            background-color: #fbe9e7;
            padding: 30px;
            border-radius: 10px;
        }

        .top-text {
            font-size: 30px;
            font-weight: bold;
            color: #006064;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Manual Entry Data Label (Brandie's Values)
st.markdown("""
    <div class="top-section">
        <div class="top-text">Manual Entry Data</div>
    </div>
""", unsafe_allow_html=True)

# Convert Date column to datetime
df1['Date'] = pd.to_datetime(df1['Date'])

# Add a new column for Day of Week
df1['Day of Week'] = df1['Date'].dt.day_name()

# Filter data based on selected date range
df1 = df1[(df1["Date"] >= date1) & (df1["Date"] <= date2)].copy()

# Define visitor categories
visitor_categories = ['Total Visitors', 'Cruise', 'Local', 'Northwest BC', 'Other', 'D/n pay - Family Pass', 'Unwilling to pay/walked away']

# Select visitor category
selected_category = st.selectbox("Select visitor category", visitor_categories)

# Define special event mappings (Display Text -> DataFrame Column)
special_event_mapping = {
    'All Days': None,
    'Long Weekend': 'Long Weekend',
    'Sponsorship Weekend': 'Sponsorship Weekend',
    'Cruise Ship Day': 'Cruise Ship Day',
    'Rainy Day': 'Rainy Day',
    'Classroom Visits': 'Classroom Visits'
}

# Initialize selected_event_display (for title usage later)
selected_event_display = "All Days"  # Default value

# User selects special events (multiple allowed)
selected_events_display = st.multiselect(
    "Filter by special event(s)", 
    options=list(special_event_mapping.keys()),
    default=None
)

# Apply event filters
if selected_events_display:
    # Update display variable for title
    selected_event_display = ", ".join(selected_events_display) if len(selected_events_display) > 1 else selected_events_display[0]
    
    # Get corresponding column names
    selected_event_columns = [special_event_mapping[event] for event in selected_events_display]
    
    # Filter logic (same as before)
    valid_columns = [col for col in selected_event_columns if col in df1.columns]
    if valid_columns:
        filter_condition = df1[valid_columns].eq('Y').any(axis=1)
        df1 = df1[filter_condition]

# Later in your title code:
title=f'{selected_category} by Day of the Week' + (f' ({selected_event_display})' if selected_event_display != "All Days" else '')

# Group by Day of Week and group sum based on selected category
visitors_by_day = df1.groupby('Day of Week')[selected_category].sum().reset_index()

# Sort days properly
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
visitors_by_day['Day of Week'] = pd.Categorical(visitors_by_day['Day of Week'], categories=days_order, ordered=True)
visitors_by_day = visitors_by_day.sort_values('Day of Week')

# Plot
fig = px.bar(visitors_by_day,
             x='Day of Week',
             y=selected_category,
             title=f'{selected_category} by Day of the Week' + (f' ({selected_event_display})' if selected_event_display != 'All Days' else ''),
             labels={selected_category: 'Total Visitors'},
             color=selected_category)

st.plotly_chart(fig)

# Download data option
with st.expander("View Data of Total Visitors:"):
    st.dataframe(visitors_by_day.style.background_gradient(cmap="Greens"))
    csv = visitors_by_day.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="TotalVisitors.csv", mime="text/csv")

# Initialize visitor type columns 
all_visitor_type_columns = ['Babies (0-3yrs)', 'Child (4-12 yrs)', 'Youth (13-18 yrs)', 'Adult/Seniors', 'Sponsors']
visitor_type_columns = [col for col in all_visitor_type_columns if col in df1.columns]

if visitor_type_columns:
    # Melt the dataframe to a long format 
    visitor_types_df = df1[visitor_type_columns].copy()
    visitor_types_melted = visitor_types_df.melt(var_name='Visitor Type', value_name='Count')

    # Group and sum counts
    visitor_types_summary = visitor_types_melted.groupby('Visitor Type')['Count'].sum().reset_index()

    # Plot bar chart
    fig = px.bar(
        visitor_types_summary,
        x='Visitor Type',
        y='Count',
        color='Visitor Type',
        title='Total Visitors by Type',
        labels={'Count': 'Number of Visitors'},
        text_auto='.2s'
    )

    fig.update_layout(
        xaxis_title='Visitor Type',
        yaxis_title='Total Count',
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig)
else:
    st.warning("⚠️ Visitor type columns not found in admissions data.")

# Create graph for Total CAD over time 
# Let user choose grouping: Monthly or Yearly
group_option = st.selectbox("Group by", ["Monthly", "Yearly"], key="group_by_sales")

# Ensure 'Date' column is in datetime format
df1['Date'] = pd.to_datetime(df1['Date'])

# Clean 'Total CAD' column and convert to float
df1['Total CAD'] = df1['Total CAD'].replace(r'[\$,]', '', regex=True).astype(float)

# Create 'Period' column based on grouping option
if group_option == "Monthly":
    df1['Period'] = df1['Date'].dt.to_period('M').astype(str)
    title = "Total CAD by Month (Square Transactions)"
elif group_option == "Yearly":
    df1['Period'] = df1['Date'].dt.year.astype(str)
    title = "Total CAD by Year (Square Transactions)"

# Group and sum Total CAD
sales_by_period = df1.groupby('Period')['Total CAD'].sum().reset_index()

# Plot bar chart
fig = px.bar(
    sales_by_period,
    x='Period',
    y='Total CAD',
    title=title,
    labels={'Period': 'Time Period', 'Total CAD': 'Total CAD ($)'},
    color='Total CAD',
    text_auto='.2s'
)

fig.update_layout(
    xaxis_title='Period',
    yaxis_title='Total CAD ($)',
    xaxis_tickangle=-45
)

st.plotly_chart(fig)
