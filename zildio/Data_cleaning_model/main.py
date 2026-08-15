import pandas as pd

from Data_cleaning_main import clean_sales_data


df_sales = pd.read_csv(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio/Data/sales_history.csv"
)

df_products = pd.read_csv(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio/Data/sku_master.csv"
)


df_sales_cleaned = clean_sales_data(
    df_sales,
    df_products
)


print(df_sales_cleaned.head())