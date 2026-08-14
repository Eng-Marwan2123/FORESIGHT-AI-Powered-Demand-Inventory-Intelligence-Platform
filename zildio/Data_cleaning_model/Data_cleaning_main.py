import pandas as pd


df_sales = pd.read_csv("C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Data\\sales_history.csv")

# clean the sales data

# 1 - dates
    
# formating the dates
df_sales["sale_date"] = pd.to_datetime(
    df_sales["sale_date"],
    format="mixed",
    errors="coerce"
)

# formate the sale_date column to datetime format and replace any NaT values with a default date
df_sales["sale_date"] = df_sales["sale_date"].fillna(pd.Timestamp("2020-01-01"))

# only selecting the date from the date the business started to today only
df_sales = df_sales[
    (df_sales["sale_date"] >= "2020-01-01") &
    (df_sales["sale_date"] <= pd.Timestamp.today())
]

# ==========================================================
# 2 - order id
# ==========================================================

# removing any rows with missing order_id values
df_sales.dropna(subset=["order_id"], inplace=True)

# removing any duplicate order_id values
df_sales.drop_duplicates(subset=["order_id"], inplace=True)

# drop the order if the sku is not in the product list
df_products = pd.read_csv("C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Data\\sku_master.csv")

df_sales = df_sales[df_sales["sku_id"].isin(df_products["sku_id"])]

# ==========================================================
# 3 - quantity
# ==========================================================

# removing any rows with missing quantity values
df_sales.dropna(subset=["quantity"], inplace=True)

# removing any rows with quantity values less than or equal to zero
df_sales = df_sales[df_sales["quantity"] > 0]

# ==========================================================
# 4 - revenue
# ==========================================================

# removing any rows with missing revenue values
df_sales.dropna(subset=["revenue"], inplace=True)

# if the revenue is minus it will be replaced with absolute value
df_sales["revenue"] = df_sales["revenue"].abs()

# removing any rows where revenue equals zero
df_sales = df_sales[df_sales["revenue"] != 0]

# ==========================================================
# 5 - discount_pct
# ==========================================================

# removing any rows with missing discount_pct values
df_sales["discount_pct"] = df_sales["discount_pct"].fillna(0)

# if the discount_pct is minus it will be replaced with absolute value
df_sales["discount_pct"] = df_sales["discount_pct"].abs()

# if discount is greater than 100 replace it with 100
df_sales.loc[df_sales["discount_pct"] > 100, "discount_pct"] = 100

# ==========================================================
# 6 - revenue
# ==========================================================

# if revenue is missing calculate it
df_sales["revenue"] = df_sales["revenue"].fillna(
    df_sales["quantity"]
    * df_sales["unit_price"]
    * (1 - df_sales["discount_pct"] / 100)
)

# ==========================================================
# 7 - region
# ==========================================================

# if the region is missing will be replaced with "Unknown"
df_sales["region"] = df_sales["region"].fillna("Unknown")

# remove spaces and convert to upper case
df_sales["region"] = df_sales["region"].str.strip().str.upper()

# ==========================================================
# 8 - channel
# ==========================================================

# if the channel is missing will be replaced with "Unknown"
df_sales["channel"] = df_sales["channel"].fillna("Unknown")

# remove spaces and convert to upper case
df_sales["channel"] = df_sales["channel"].str.strip().str.upper()

# ==========================================================
# 9 - shipping days
# ==========================================================

# shipping days can't be negative
df_sales["shipping_days"] = df_sales["shipping_days"].abs()

# replace missing shipping days with 0 and the shipping status is canceled replace the shipping days with 0
df_sales.loc[
    df_sales["order_status"] == "Canceled",
    "shipping_days"
] = 0
#if missing the shipping days will be replaced with 0
df_sales["shipping_days"] = df_sales["shipping_days"].fillna(0)


# 10 payment_method

# if the payment_method is missing will be replaced with "Unknown"
df_sales["payment_method"] = df_sales["payment_method"].fillna("Unknown")

# remove spaces and convert to upper case
df_sales["payment_method"] = df_sales["payment_method"].str.strip().str.upper()

# order_status

# if the order_status is missing will be replaced with "Unknown"

df_sales["order_status"] = df_sales["order_status"].fillna("Unknown")

# remove spaces and convert to upper case
df_sales["order_status"] = df_sales["order_status"].str.strip().str.upper()

#sales_rep

# if the sales_rep is missing will be replaced with "Unknown"

df_sales["sales_rep"] = df_sales["sales_rep"].fillna("Unknown")

# remove spaces and convert to upper case
df_sales["sales_rep"] = df_sales["sales_rep"].str.strip().str.upper()

# warehouse
df_sales["warehouse"] = df_sales["warehouse"].fillna("Unknown")

# remove spaces and convert to upper case
df_sales["warehouse"] = df_sales["warehouse"].str.strip().str.upper()

# save cleaned data
if not df_sales.empty:
    df_sales.to_csv("C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Cleaned_data\\sales_history_cleaned.csv", index=False )      
    print("done")
else : 
    print("failed");


