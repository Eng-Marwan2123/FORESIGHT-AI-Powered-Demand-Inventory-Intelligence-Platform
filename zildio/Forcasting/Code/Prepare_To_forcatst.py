# this code will arranged the cleaned data to be ready for qunatiny and sales for casting 
# Month || SKU || quntatiy || revenue 
import pandas as pd

df = pd.read_csv("C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Cleaned_data\\sales_history_cleaned.csv")

df["sale_date"] = pd.to_datetime(df["sale_date"],)

df["Month_date"] = df["sale_date"].dt.to_period("M")

# Group by SKU and month  and sum quantity
monthly_sales = (
    df.groupby([ "sku_id","Month_date"])["quantity"]
      .sum()
      .reset_index()
)

# Save the prepared data
monthly_sales.to_csv(
    "C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Forcasting\\Data\\monthly_sales.csv",
    index=False
)