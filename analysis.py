import pandas as pd

bank_name = "MT&T Bank"

net_income = 2000
print(net_income)

average_assets = 200000
return_on_assets_Y1 = net_income / average_assets
print(return_on_assets_Y1)
print(f"Return on Assets: {return_on_assets_Y1:.1%}")

net_income_Y2 = 2400
average_assets_Y2 = 200000
return_on_assets_Y2 = net_income_Y2 / average_assets_Y2
print(return_on_assets_Y2)
print(f"Return on Assets: {return_on_assets_Y2:.1%}")

#Task11: Automating financial calculations with a loop

net_income = {                 #variable reassignment-reusing the variable name
    2023: 2741,
    2024: 2588,
    2025: 2851
}
for year, income in net_income.items():
    print(year, income)

income_growth_2025 = (net_income[2025] - net_income[2024]) / net_income[2024]
print(f"Income Growth from 2024 to 2025: {income_growth_2025:.2%}") 

#Task 13: Automate growth calculations for every year
for year in range(2024, 2026):
    previous_year_income = net_income[year - 1]
    current_year_income = net_income[year]
    growth_rate = (current_year_income - previous_year_income) / previous_year_income
    print(f"Income Growth from {year - 1} to {year}: {growth_rate:.2%}")

df = pd.DataFrame(list(net_income.items()), columns=['Year', 'Net Income'])
print(df)

#Task 19: Calculate growth using pandas
# .pct_change() --> how pandas canperform the same calculation across an entire column with a single instruction.

df['Income Growth (%)'] = df['Net Income'].pct_change() * 100
print(df)

