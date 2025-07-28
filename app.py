import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

@st.cache_data(ttl=3600)
def load_data(csv_path='data_scientist_jobs.csv'):
    """
    Load the job data CSV and parse date columns.
    Cached for one hour to reduce I/O overhead.
    """
    df = pd.read_csv(csv_path, parse_dates=['scraped_at', 'date_posted'])
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    return df

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Load data on each run or cache expire
df = load_data()

# Sidebar filters
st.sidebar.title("Filters")
companies = ['All'] + sorted(df['company_name'].unique())
locations = ['All'] + sorted(df['location'].unique())

selected_company = st.sidebar.selectbox("Company", companies)
selected_location = st.sidebar.selectbox("Location", locations)
start_date, end_date = st.sidebar.date_input(
    "Date range (by Date Posted)",
    [df['date_posted'].dt.date.min(), df['date_posted'].dt.date.max()]
)

# Apply filters to the DataFrame
df_filtered = df.copy()
if selected_company != 'All':
    df_filtered = df_filtered[df_filtered['company_name'] == selected_company]
if selected_location != 'All':
    df_filtered = df_filtered[df_filtered['location'] == selected_location]

df_filtered = df_filtered[
    (df_filtered['date_posted'].dt.date >= start_date) &
    (df_filtered['date_posted'].dt.date <= end_date)
]

# Page title
st.title("📊 Data Scientist Job Dashboard")

# Line chart: open positions by date_posted
grouped = (
    df_filtered.groupby(df_filtered['date_posted'].dt.date)
    .size()
    .reset_index(name='count')
)
grouped.rename(columns={'date_posted': 'date'}, inplace=True)
fig_line = px.line(
    grouped,
    x='date',
    y='count',
    title='Total Open Positions by Date Posted'
)
st.plotly_chart(fig_line, use_container_width=True)

# Bar chart: postings by location
bar_data = df_filtered['location'].value_counts().reset_index()
bar_data.columns = ['location', 'count']
fig_bar = px.bar(
    bar_data,
    x='location',
    y='count',
    title='Postings by Location'
)
st.plotly_chart(fig_bar, use_container_width=True)

# Data table with clickable links
st.subheader("🔍 Job Listings")
def make_clickable(url):
    """Return HTML for clickable link in table."""
    return f"<a target='_blank' href='{url}'>Link</a>"

table = df_filtered[
    ['job_title', 'company_name', 'location', 'date_posted', 'url', 'source']
].copy()
table['link'] = table['url'].apply(make_clickable)
st.write(
    table.to_html(escape=False, index=False),
    unsafe_allow_html=True
)

# Footer with last refresh timestamp
st.markdown(
    f"*Last data load: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
)
