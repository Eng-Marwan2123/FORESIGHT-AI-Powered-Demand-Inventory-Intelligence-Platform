from prophet import Prophet
import pandas as pd


def forecast_sales(df):

    # Make a copy so the original DataFrame is not modified
    df = df.copy()

    # 1 - CONVERT SALE DATE

    df["sale_date"] = pd.to_datetime(
        df["sale_date"],
        errors="coerce"
    )

    # Remove invalid dates
    df = df.dropna(
        subset=["sale_date"]
    )

    # 2 - CREATE MONTH

    df["Month_date"] = df["sale_date"].dt.to_period("M")

    # 3 - GROUP SALES BY SKU AND MONTH

    monthly_sales = (
        df.groupby(
            ["sku_id", "Month_date"]
        )["quantity"]
        .sum()
        .reset_index()
    )

    # 4 - PREPARE DATA FOR PROPHET

    monthly_sales = monthly_sales.rename(
        columns={
            "Month_date": "ds",
            "quantity": "y"
        }
    )

    # Convert Period to datetime
    monthly_sales["ds"] = (
        monthly_sales["ds"]
        .dt.to_timestamp()
    )

    # 5 - FORECAST EACH SKU

    all_forecasts = []

    for sku in monthly_sales["sku_id"].unique():

        sku_data = monthly_sales[
            monthly_sales["sku_id"] == sku
        ][["ds", "y"]].copy()

        # Sort by date
        sku_data = sku_data.sort_values("ds")

        # Prophet needs historical observations
        if len(sku_data) < 2:
            print(
                f"Skipping {sku}: not enough historical data"
            )
            continue

        # PROPHET MODEL

        model = Prophet()

        model.fit(sku_data)

        # CREATE FUTURE 3 MONTHS

        future = model.make_future_dataframe(
            periods=3,
            freq="MS"
        )

        # MAKE FORECAST

        forecast = model.predict(future)

        # Keep only required columns
        forecast = forecast[
            ["ds", "yhat"]
        ]

        # Add SKU
        forecast["sku_id"] = sku

        all_forecasts.append(
            forecast
        )

    # 6 - COMBINE ALL SKU FORECASTS

    if not all_forecasts:
        return pd.DataFrame(
            columns=["ds", "yhat", "sku_id"]
        )

    final_forecast = pd.concat(
        all_forecasts,
        ignore_index=True
    )
    print(type(final_forecast))
    print(final_forecast.shape)
    print(final_forecast.columns)
    final_forecast.to_csv("/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio/Forcasting/forecasted_sales.csv",index=False)
    return final_forecast
    # Save to postgress 
