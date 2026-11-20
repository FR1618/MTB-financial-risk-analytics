import pandas as pd

data = {
    "Year": [2024,2024,2024,2024,
             2025,2025,2025,2025],
    "Quarter": ["Q1","Q2","Q3","Q4",
                "Q1","Q2","Q3","Q4"],
    "Net Income": [580, 620, 680, 708,
                   650, 700, 720, 781]
}


df = pd.DataFrame(data) 
print(df)

annual_income = df.groupby('Year')['Net Income'].sum()
print(annual_income)

annual_income_growth = annual_income.pct_change() * 100
print(annual_income_growth)

#For each year, what were the total, average, highest, and lowest quarterly net income figures?
quarterly_summary = df.groupby('Year')['Net Income'].agg(['sum', 'mean', 'max', 'min'])
print(quarterly_summary)

import plotly.express as px

fig = px.bar(
    df, 
    x='Quarter', 
    y='Net Income', 
    color= df['Year'].astype(str), 
    barmode='group',
    title='Quarterly Net Income Comparison'

    )

fig.show()
