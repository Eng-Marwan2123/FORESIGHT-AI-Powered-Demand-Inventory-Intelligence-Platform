import pandas as pd

# IMPORTING THE CLEANED INVENTORY DATA AND FORECASTED DATA
df_inventory = pd.read_csv(
    "C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Data\\inventory_snapshots.csv"
)

df_forecast = pd.read_csv(
    "C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Forcasting\\Data\\prophet_forecast.csv"
)

# Convert date to datetime
df_inventory['date'] = pd.to_datetime(df_inventory['date'])

# Sort by SKU and date
df_inventory = df_inventory.sort_values(
    ['sku_id', 'date']
)

# Calculate total stock
df_inventory['Total_stock'] = (
    df_inventory['on_hand_units'] +
    df_inventory['on_order_units']
)

# Get the latest inventory snapshot for each SKU
df_inventory    = (
    df_inventory
    .groupby('sku_id')
    .last()
    .reset_index()
)

df_inventory = df_inventory[['sku_id', 'date', 'Total_stock']]
#grouped_inventory = grouped_inventory[['sku_id', 'date', 'Total_stock']]
df_inventory.to_csv("C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Rick _Mangment\\Data\\cleaned_inventory.csv",index=False )


df_forecast = df_forecast.sort_values(
    ['sku_id', 'ds']
)

df_forecast = (
    df_forecast
    .groupby('sku_id').sum()
) 

forecast_demand = (
    df_forecast
    .groupby('sku_id')['yhat']
    .sum()
    .reset_index()
)

forecast_demand = forecast_demand.rename(
    columns={'yhat': 'Forecast_demand'}
)
print(forecast_demand)