import streamlit as st
import plotly.express as px


st.title("MT&T Bank Financial Analysis")

st.write("Interactive Financial Performance Dashboard for MT&T Bank")
import pandas as pd

data = {
    "Year": [2024, 2024, 2024, 2024,
             2025, 2025, 2025, 2025],
    "Quarter": ["Q1", "Q2", "Q3", "Q4",
                "Q1", "Q2", "Q3", "Q4"],
    "Net Income": [580, 620, 680, 708,
                   650, 700, 720, 781]
}

df = pd.DataFrame(data)

st.dataframe(df) 
selected_year = st.selectbox(          #st.selectbox() --> creates a dropdown menu for user selection
    "Select Reporting Year",
    options=sorted(df['Year'].unique())   #.unique() --> returns the unique values in a column/distinct years in a dataset
) 
# 1. Filter the financial data
filtered_data = df[df['Year'] == selected_year]
# 2. Display the filtered table
st.subheader(f"Financial Data for {selected_year}")
st.dataframe(filtered_data)
# 3. Add the chart selector 
chart_type = st.selectbox(
    "Select Chart Type",
    options=["Bar Chart", "Line Chart"]
)
if chart_type == "Bar Chart":
    fig = px.bar(filtered_data, 
                 x='Quarter', 
                 y='Net Income', 
                 title=f'Net Income by Quarter for {selected_year}',
                 labels={'Net Income': 'Net Income (in millions)'}
    )
else:
    fig = px.line(filtered_data, 
                  x='Quarter', 
                  y='Net Income', 
                  title=f'Net Income by Quarter for {selected_year}',
                  labels={'Net Income': 'Net Income (in millions)'}
    )   

st.plotly_chart(fig, width="stretch")  # Display the bar chart using Plotly


#Task 8 — Financial KPI Cards

total_income = filtered_data['Net Income'].sum()      # step1

# step2
#Deleted the standalone st.metric in streamlit and replaced it with a horizontal arrangement of KPI cards using st.columns(). This allows for a more organized and visually appealing display of key financial metrics.

#financial dashboard. Task 8 — Step 5: Arrange KPI cards horizontally
total_income = filtered_data['Net Income'].sum()      
average_income = filtered_data['Net Income'].mean()
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Total Net Income",                 
              value=f"${total_income:,.0f}M"            
    )       

with col2:
    st.metric(label="Average Net Income",
              value=f"${average_income:,.0f}M"
    )   

#Task 9 — Quarter-over-Quarter (QoQ) Growth
#The formula is: 
# QoQ Growth = (Current Quarter Net Income - Previous Quarter Net Income) / Previous Quarter Net Income * 100
#Step 1: Calculate QoQ Growth

filtered_data = df[df['Year'] == selected_year]
filtered_data = filtered_data.copy()  # Create a copy of the filtered data to avoid SettingWithCopyWarning - independent copy of the filtered data
filtered_data['QoQ Growth'] = filtered_data['Net Income'].pct_change() * 100  # Calculate QoQ Growth as a percentage    
#Step 3: Display QoQ growth
st.dataframe(
    filtered_data,
    column_config={
        "QoQ Growth": st.column_config.NumberColumn(
            format="%.2f%%"
        )
    }
)

# %.2f displays a number with two decimal places. --> %% displays a literal percentage symbol.

annual_income = df.groupby('Year')['Net Income'].sum() # Group by Year and sum Net Income
annual_growth = annual_income.pct_change() * 100  # Calculate annual growth as a percentage
annual_summary = pd.DataFrame({
    "Annual Net Income ($M)": annual_income,
    "Annual Growth (%)": annual_growth
})

st.subheader("Year-over-Year Financial Performance")
st.dataframe(annual_summary)

annual_fig = px.bar(
    annual_summary.reset_index(),
    x='Year',
    y='Annual Net Income ($M)',
    title='Annual Net Income by Year',
    labels={'Annual Net Income ($M)': 'Annual Net Income (in millions)'}
)

st.plotly_chart(annual_fig, width="stretch")  # Display the annual net income bar chart using Plotly    
