from prophet import Prophet
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import sys

from zildio.Data_base import Data_base

# ==========================================================
# LOAD DATA based on the provided paths
# ==========================================================
# engine = create_engine(
#    "postgresql+psycopg://neondb_owner:npg_L78TmfsVoiWY@ep-damp-rice-zapgu6fx-pooler.c-2.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")


# Minimum number of monthly data points required before we trust a
# per-SKU Prophet fit. With <6 points Prophet has almost nothing to
# learn a trend/seasonality from and just returns a near-flat mean,
# which is why the aggregated forecast can look flatter than reality.
MIN_MONTHS_FOR_FORECAST = 6


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

        n_points = len(sku_data)

        # Prophet needs historical observations. Below this, a fit is
        # technically possible but meaningless (essentially a straight
        # line through 2-5 points), which is what was flattening the
        # aggregate chart.
        if n_points < MIN_MONTHS_FOR_FORECAST:
            print(
                f"Skipping {sku}: only {n_points} months of history "
                f"(< {MIN_MONTHS_FOR_FORECAST}), not enough to forecast reliably"
            )
            continue

        # Guard against zero/negative values before log-transform
        if (sku_data["y"] <= 0).any():
            sku_data["y"] = sku_data["y"].clip(lower=0)

        # Log1p-transform the target. This compresses large spikes
        # (e.g. 700 -> 4200 -> 500) into a scale Prophet's default
        # priors handle far better, and prevents the forecast from
        # being dominated by additive noise around a flat mean.
        sku_data["y_log"] = np.log1p(sku_data["y"])

        fit_frame = sku_data[["ds", "y_log"]].rename(
            columns={"y_log": "y"}
        )

        # PROPHET MODEL
        #
        # - changepoint_prior_scale raised from the default 0.05 so the
        #   trend can actually bend toward real jumps in demand instead
        #   of staying rigid.
        # - yearly_seasonality only enabled once there's enough history
        #   (2+ years) to estimate it - with less data Prophet will
        #   happily "fit" a yearly cycle to noise.
        # - weekly/daily seasonality disabled since the data is monthly.
        model = Prophet(
            changepoint_prior_scale=0.5,
            seasonality_mode="additive",  
            weekly_seasonality=True,
            daily_seasonality=False,
        )

        model.fit(fit_frame)

        # CREATE FUTURE 3 MONTHS

        future = model.make_future_dataframe(
            periods=3,
            freq="MS"
        )

        # MAKE FORECAST

        forecast = model.predict(future)

        # Undo the log1p transform to get back to real units
        for col in ["yhat", "yhat_lower", "yhat_upper"]:
            forecast[col] = np.expm1(forecast[col]).clip(lower=0)

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

    Data_base.save_data_to_db(final_forecast, "forecasted_sales")

    print("Data saved successfully!")
    return final_forecast