import pandas as pd
from sqlalchemy import create_engine, text
import sys

from zildio.Data_base import Data_base


# ==========================================================
# LOAD DATA based on the provided paths
# ==========================================================
#engine = create_engine(
 #   "postgresql+psycopg://neondb_owner:npg_L78TmfsVoiWY@ep-damp-rice-zapgu6fx-pooler.c-2.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")


def calculate_inventory_risk(df_inventory, df_forecast):

    # Make copies
    df_inventory = df_inventory.copy()
    df_forecast = df_forecast.copy()

    print("RISK MANAGEMENT STARTED")
    print("Inventory columns:", df_inventory.columns.tolist())
    print("Forecast columns:", df_forecast.columns.tolist())

    # -----------------------------
    # INVENTORY
    # -----------------------------

    df_inventory["date"] = pd.to_datetime(
        df_inventory["date"],
        errors="coerce"
    )

    df_inventory["sku_id"] = (
        df_inventory["sku_id"]
        .astype(str)
    )

    df_inventory["on_hand_units"] = pd.to_numeric(
        df_inventory["on_hand_units"],
        errors="coerce"
    ).fillna(0)

    df_inventory["on_order_units"] = pd.to_numeric(
        df_inventory["on_order_units"],
        errors="coerce"
    ).fillna(0)

    df_inventory["lead_time_days"] = pd.to_numeric(
        df_inventory["lead_time_days"],
        errors="coerce"
    ).fillna(0)

    df_inventory["reorder_point"] = pd.to_numeric(
        df_inventory["reorder_point"],
        errors="coerce"
    ).fillna(0)

    # Total stock
    df_inventory["Total_stock"] = (
        df_inventory["on_hand_units"]
        + df_inventory["on_order_units"]
    )

    # Latest snapshot per SKU
    df_inventory = (
        df_inventory
        .sort_values(["sku_id", "date"])
        .groupby("sku_id", as_index=False)
        .last()
    )

    df_inventory = df_inventory[
        [
            "sku_id",
            "date",
            "Total_stock",
            "lead_time_days",
            "reorder_point"
        ]
    ]

    # -----------------------------
    # FORECAST
    # -----------------------------

    df_forecast["ds"] = pd.to_datetime(
        df_forecast["ds"],
        errors="coerce"
    )

    df_forecast["sku_id"] = (
        df_forecast["sku_id"]
        .astype(str)
    )

    df_forecast["yhat"] = pd.to_numeric(
        df_forecast["yhat"],
        errors="coerce"
    )

    df_forecast = df_forecast.dropna(
        subset=["sku_id", "ds", "yhat"]
    )

    # Total forecast demand per SKU
    forecast_demand = (
        df_forecast
        .groupby("sku_id")["yhat"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "yhat": "Forecast_demand"
            }
        )
    )

    # -----------------------------
    # MERGE
    # -----------------------------

    coverage_ratio = pd.merge(
        df_inventory,
        forecast_demand,
        on="sku_id",
        how="left"
    )

    coverage_ratio["Forecast_demand"] = (
        coverage_ratio["Forecast_demand"]
        .fillna(0)
    )

    # -----------------------------
    # COVERAGE
    # (guarded against division by zero when Forecast_demand == 0)
    # -----------------------------

    coverage_ratio["Coverage"] = (
        coverage_ratio["Total_stock"]
        / coverage_ratio["Forecast_demand"].replace(0, pd.NA)
    )

    # -----------------------------
    # LEAD TIME SCORE
    # Shorter lead time = faster to replenish = LOWER stockout risk.
    # Longer lead time = slower to replenish = HIGHER stockout risk.
    # -----------------------------

    def score_lead_time(lead_time):

        if lead_time <= 7:
            return 1
        elif lead_time <= 14:
            return 2
        elif lead_time <= 21:
            return 3
        elif lead_time <= 28:
            return 4
        else:
            return 5

    coverage_ratio["Lead_Time_Points"] = (
        coverage_ratio["lead_time_days"]
        .apply(score_lead_time)
    )

    # -----------------------------
    # COVERAGE SCORE (stockout side)
    # Low coverage relative to demand = HIGH stockout risk.
    # NaN coverage (zero forecast demand) treated as max risk (4),
    # since any demand at all would immediately exceed zero-forecast stock.
    # -----------------------------

    def classify_coverage(coverage):

        if pd.isna(coverage):
            return 4
        elif coverage < 0.5:
            return 4
        elif coverage < 1:
            return 3
        elif coverage < 2:
            return 2
        else:
            return 1

    coverage_ratio["Coverage_Rating"] = (
        coverage_ratio["Coverage"]
        .apply(classify_coverage)
    )

    # -----------------------------
    # STOCKOUT RISK
    # -----------------------------

    coverage_ratio["Total_Points"] = (
        coverage_ratio["Lead_Time_Points"]
        + coverage_ratio["Coverage_Rating"]
    )

    coverage_ratio["Stockout_Risk"] = (
        coverage_ratio["Total_Points"] / 9
    )

    # -----------------------------
    # OVERSTOCK SCORE
    # How far Total_stock sits above reorder_point, relative to
    # reorder_point itself. Guarded against reorder_point == 0.
    # -----------------------------

    coverage_ratio["Excess_Ratio"] = (
        (coverage_ratio["Total_stock"] - coverage_ratio["reorder_point"])
        / coverage_ratio["reorder_point"].replace(0, pd.NA)
    )

    def classify_overstock(excess_ratio):

        if pd.isna(excess_ratio):
            # No usable reorder point to compare against — no signal either way
            return 1
        elif excess_ratio < 0.5:
            return 1
        elif excess_ratio < 1:
            return 2
        elif excess_ratio < 2:
            return 3
        elif excess_ratio < 4:
            return 4
        else:
            return 5

    coverage_ratio["Overstock_Points"] = (
        coverage_ratio["Excess_Ratio"]
        .apply(classify_overstock)
    )

    # Normalized 0-1, same scale as Stockout_Risk, so both axes are
    # directly comparable on a scatter chart.
    coverage_ratio["overstock_risk"] = (
        coverage_ratio["Overstock_Points"] / 5
    )

    # -----------------------------
    # ACTION
    # Row-wise, since this needs both Stockout_Risk and overstock_risk
    # at the same time — a plain column .apply() only ever sees one
    # column's values, so this must run with axis=1 to receive the
    # full row.
    # -----------------------------

    def action_from_risk(row):

        stockout = row["Stockout_Risk"]
        overstock = row["overstock_risk"]

        if stockout <= 0.35 and overstock <= 0.6:
            return "Overstock"
        elif stockout <= 0.60:
            return "Fine"
        elif stockout <= 0.85:
            return "Monitor"
        else:
            return "Order ASAP"

    coverage_ratio["Action"] = coverage_ratio.apply(
        action_from_risk,
        axis=1
    )

    #save to PostgreSQL
    Data_base.save_data_to_db(coverage_ratio,"inventory_risk")

    print("Data saved successfully!")

    # -----------------------------
    # RETURN
    # -----------------------------

    return coverage_ratio[
        [
            "sku_id",
            "Total_stock",
            "lead_time_days",
            "reorder_point",
            "Forecast_demand",
            "Coverage",
            "Coverage_Rating",
            "Stockout_Risk",
            "overstock_risk",
            "Action"
        ]
    ]