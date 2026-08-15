import pandas as pd
import sys


# ============================================================
# DATA CLEANING MODULE
# ============================================================

sys.path.append(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/"
    "zildio/Data_cleaning_model"
)

import Data_cleaning_main


# ============================================================
# FORECASTING MODULE
# ============================================================

sys.path.append(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/"
    "zildio/Forcasting/Code"
)

import forcasting


# ============================================================
# RISK MANAGEMENT MODULE
# ============================================================

sys.path.append(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/"
    "zildio/Risk_Mangment/Code"
)

import Risk_managment


# ============================================================
# CHECK WHICH RISK FILE PYTHON IS USING
# ============================================================

print("\nRisk Management module:")
print(Risk_managment.__file__)


# ============================================================
# LOAD DATA
# ============================================================

df_sales = pd.read_csv(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/"
    "zildio/Data/sales_history.csv"
)

df_products = pd.read_csv(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/"
    "zildio/Data/sku_master.csv"
)

df_inventory = pd.read_csv(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/"
    "zildio/Data/inventory_snapshots.csv"
)


# ============================================================
# DATA CLEANING
# ============================================================

Cleaned_sales = Data_cleaning_main.clean_sales_data(
    df_sales,
    df_products
)


# ============================================================
# FORECASTING
# ============================================================

forecasted_sales = forcasting.forecast_sales(
    Cleaned_sales
)


# ============================================================
# DEBUG FORECAST
# ============================================================

print("\nForecast shape:")
print(forecasted_sales.shape)

print("\nForecast columns:")
print(forecasted_sales.columns)

print("\nForecast sample:")
print(forecasted_sales.head())


# ============================================================
# DEBUG INVENTORY
# ============================================================

print("\nInventory columns:")
print(df_inventory.columns)

print("\nInventory sample:")
print(df_inventory.head())


# ============================================================
# INVENTORY RISK
# ============================================================

inventory_risk = Risk_managment.calculate_inventory_risk(
    df_inventory,
    forecasted_sales
)


# ============================================================
# RESULTS
# ============================================================

print("\n========================================")
print("Cleaned Sales Data:")
print("========================================")
print(Cleaned_sales.head())


print("\n========================================")
print("Forecasted Sales Data:")
print("========================================")
print(forecasted_sales.head())


print("\n========================================")
print("Inventory Risk Data:")
print("========================================")
print(inventory_risk)
