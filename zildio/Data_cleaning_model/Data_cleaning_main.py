import pandas as pd
from sqlalchemy import create_engine, text
import sys
sys.path.append(
    "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio/Data_base"
)

import Data_base
# ==========================================================
# LOAD DATA based on the provided paths
# ==========================================================
#engine = create_engine(
 #   "postgresql+psycopg://neondb_owner:npg_L78TmfsVoiWY@ep-damp-rice-zapgu6fx-pooler.c-2.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")


# ==========================================================
# CLEAN SALES DATA FUNCTION
# ==========================================================

def clean_sales_data(df_sales, df_products):

    # Make a copy so the original DataFrame is not modified
    df_sales = df_sales.copy()
    df_products = df_products.copy()

    # ======================================================
    # 1 - DATE
    # ======================================================

    # Format sale_date as datetime
    df_sales["sale_date"] = pd.to_datetime(
        df_sales["sale_date"],
        format="mixed",
        errors="coerce"
    )

    # Replace invalid/missing dates with default date
    df_sales["sale_date"] = df_sales["sale_date"].fillna(
        pd.Timestamp("2020-01-01")
    )

    # Keep dates between business start date and today
    df_sales = df_sales[
        (df_sales["sale_date"] >= pd.Timestamp("2020-01-01")) &
        (df_sales["sale_date"] <= pd.Timestamp.today())
    ]

    # ======================================================
    # 2 - ORDER ID
    # ======================================================

    # Remove rows with missing order_id
    df_sales.dropna(
        subset=["order_id"],
        inplace=True
    )

    # Remove duplicate orders
    df_sales.drop_duplicates(
        subset=["order_id"],
        inplace=True
    )

    # Keep only SKUs that exist in the product master
    df_sales = df_sales[
        df_sales["sku_id"].isin(df_products["sku_id"])
    ]

    # ======================================================
    # 3 - QUANTITY
    # ======================================================

    # Convert quantity to numeric
    df_sales["quantity"] = pd.to_numeric(
        df_sales["quantity"],
        errors="coerce"
    )

    # Remove missing quantity
    df_sales.dropna(
        subset=["quantity"],
        inplace=True
    )

    # Remove quantity <= 0
    df_sales = df_sales[
        df_sales["quantity"] > 0
    ]

    # ======================================================
    # 4 - UNIT PRICE
    # ======================================================

    # Convert unit_price to numeric
    df_sales["unit_price"] = pd.to_numeric(
        df_sales["unit_price"],
        errors="coerce"
    )

    # ======================================================
    # 5 - DISCOUNT PERCENTAGE
    # ======================================================

    # Convert discount_pct to numeric
    df_sales["discount_pct"] = pd.to_numeric(
        df_sales["discount_pct"],
        errors="coerce"
    )

    # Missing discount = 0
    df_sales["discount_pct"] = df_sales[
        "discount_pct"
    ].fillna(0)

    # Negative discount -> positive
    df_sales["discount_pct"] = df_sales[
        "discount_pct"
    ].abs()

    # Maximum discount = 100%
    df_sales.loc[
        df_sales["discount_pct"] > 100,
        "discount_pct"
    ] = 100

    # ======================================================
    # 6 - REVENUE
    # ======================================================

    # Convert revenue to numeric
    df_sales["revenue"] = pd.to_numeric(
        df_sales["revenue"],
        errors="coerce"
    )

    # Calculate missing revenue
    calculated_revenue = (
        df_sales["quantity"]
        * df_sales["unit_price"]
        * (1 - df_sales["discount_pct"] / 100)
    )

    df_sales["revenue"] = df_sales["revenue"].fillna(
        calculated_revenue
    )

    # Convert negative revenue to positive
    df_sales["revenue"] = df_sales["revenue"].abs()

    # Remove revenue = 0
    df_sales = df_sales[
        df_sales["revenue"] != 0
    ]

    # Remove rows where revenue is still missing
    df_sales.dropna(
        subset=["revenue"],
        inplace=True
    )

    # ======================================================
    # 7 - REGION
    # ======================================================

    # Missing region = Unknown
    df_sales["region"] = df_sales[
        "region"
    ].fillna("Unknown")

    # Remove spaces and convert to uppercase
    df_sales["region"] = (
        df_sales["region"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ======================================================
    # 8 - CHANNEL
    # ======================================================

    # Missing channel = Unknown
    df_sales["channel"] = df_sales[
        "channel"
    ].fillna("Unknown")

    # Remove spaces and convert to uppercase
    df_sales["channel"] = (
        df_sales["channel"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ======================================================
    # 9 - ORDER STATUS
    # ======================================================

    # Missing order status = Unknown
    df_sales["order_status"] = df_sales[
        "order_status"
    ].fillna("Unknown")

    # Remove spaces and convert to uppercase
    df_sales["order_status"] = (
        df_sales["order_status"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ======================================================
    # 10 - SHIPPING DAYS
    # ======================================================

    # Convert shipping_days to numeric
    df_sales["shipping_days"] = pd.to_numeric(
        df_sales["shipping_days"],
        errors="coerce"
    )

    # Negative shipping days -> positive
    df_sales["shipping_days"] = df_sales[
        "shipping_days"
    ].abs()

    # Canceled orders have 0 shipping days
    df_sales.loc[
        df_sales["order_status"] == "CANCELED",
        "shipping_days"
    ] = 0

    # Missing shipping days = 0
    df_sales["shipping_days"] = df_sales[
        "shipping_days"
    ].fillna(0)

    # ======================================================
    # 11 - PAYMENT METHOD
    # ======================================================

    # Missing payment method = Unknown
    df_sales["payment_method"] = df_sales[
        "payment_method"
    ].fillna("Unknown")

    # Remove spaces and convert to uppercase
    df_sales["payment_method"] = (
        df_sales["payment_method"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ======================================================
    # 12 - SALES REP
    # ======================================================

    # Missing sales rep = Unknown
    df_sales["sales_rep"] = df_sales[
        "sales_rep"
    ].fillna("Unknown")

    # Remove spaces and convert to uppercase
    df_sales["sales_rep"] = (
        df_sales["sales_rep"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ======================================================
    # 13 - WAREHOUSE
    # ======================================================

    # Missing warehouse = Unknown
    df_sales["warehouse"] = df_sales[
        "warehouse"
    ].fillna("Unknown")

    # Remove spaces and convert to uppercase
    df_sales["warehouse"] = (
        df_sales["warehouse"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ======================================================
    # RETURN RESULT
    # ======================================================

 
# ============================================================
# Uploading the data to DB 
# ============================================================
# 1 - Create a connection to the PostgreSQL database (Neon)
    # Check that your DataFrame actually contains data
    if not df_sales.empty:

        print(f"Cleaned sales rows: {len(df_sales)}")

        Data_base.save_data_to_db(
            df_sales,
            "cleaned_sales"
        )

        return df_sales

    else:

        print("ERROR: Cleaned sales DataFrame is empty.")

        return -1