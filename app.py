import os
import sys

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from sqlalchemy import create_engine, text
from dotenv import load_dotenv


# ============================================================
# PIPELINE MODULE IMPORTS
# (Cleaning / Forecasting / Risk Management live in separate
# folders in this repo - adjust these paths if your project
# structure differs)
# ============================================================
##
PROJECT_ROOT = "/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio"

for _module_path in [
    f"/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio/Data_cleaning_model",
    f"/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio/Forcasting/Code",
    f"/workspaces/FORESIGHT-AI-Powered-Demand-Inventory-Intelligence-Platform/zildio/Risk_Mangment/Code",
]:

    if _module_path not in sys.path:

        sys.path.append(_module_path)

from Data_cleaning_main import clean_sales_data
from forcasting import forecast_sales
from Risk_managment import calculate_inventory_risk
##

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FORESIGHT | Inventory Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LIGHT (WHITE / GRAY) THEME
# ============================================================

st.markdown("""
<style>

    :root {
        --ui-bg: #f5f7fa;
        --ui-panel: #ffffff;
        --ui-panel-alt: #f0f2f6;
        --ui-border: #dfe3ea;
        --ui-text: #1f2937;
        --ui-text-muted: #6b7280;
        --ui-accent: #2563eb;
        --ui-accent-alt: #16c79a;
    }

    /* App background */

    .stApp {
        background-color: var(--ui-bg);
        color: var(--ui-text);
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: var(--ui-panel);
        border-right: 1px solid var(--ui-border);
    }

    section[data-testid="stSidebar"] * {
        color: var(--ui-text);
    }

    /* Headings */

    h1, h2, h3, h4, h5, h6 {
        color: var(--ui-text) !important;
    }

    /* Body / captions */

    p, span, label, .stMarkdown, .stCaption {
        color: var(--ui-text);
    }

    /* Metrics */

    div[data-testid="stMetric"] {
        background-color: var(--ui-panel);
        border: 1px solid var(--ui-border);
        border-radius: 12px;
        padding: 14px 16px;
    }

    div[data-testid="stMetricValue"] {
        color: var(--ui-text) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--ui-text-muted) !important;
    }

    /* Buttons */

    .stButton > button {
        background-color: var(--ui-panel-alt);
        color: var(--ui-text);
        border: 1px solid var(--ui-border);
        border-radius: 8px;
    }

    .stButton > button:hover {
        border-color: var(--ui-accent);
        color: var(--ui-accent);
    }

    .stButton > button[kind="primary"] {
        background-color: var(--ui-accent);
        color: #ffffff;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: var(--ui-accent-alt);
        color: #ffffff;
    }

    /* Inputs - multiselect, selectbox, file uploader */

    div[data-baseweb="select"] > div {
        background-color: var(--ui-panel-alt);
        border-color: var(--ui-border);
        color: var(--ui-text);
    }

    section[data-testid="stFileUploaderDropzone"] {
        background-color: var(--ui-panel-alt);
        border: 1px dashed var(--ui-border);
    }

    /* Expander */

    div[data-testid="stExpander"] {
        background-color: var(--ui-panel);
        border: 1px solid var(--ui-border);
        border-radius: 12px;
    }

    /* Tabs */

    button[data-baseweb="tab"] {
        color: var(--ui-text-muted);
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--ui-accent);
    }

    /* Dataframe / table */

    div[data-testid="stDataFrame"] {
        background-color: var(--ui-panel);
        border: 1px solid var(--ui-border);
        border-radius: 12px;
    }

    /* Divider */

    hr {
        border-color: var(--ui-border) !important;
    }

    /* Status widget */

    div[data-testid="stStatusWidget"] {
        background-color: var(--ui-panel);
        border: 1px solid var(--ui-border);
        border-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# .env must be in the same folder as app.py
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ============================================================
# CHECK DATABASE URL
# ============================================================

if not DATABASE_URL:

    st.error(
        "DATABASE_URL was not found.\n\n"
        "Make sure your .env file is located in the project root "
        "and contains DATABASE_URL."
    )

    st.stop()


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_engine():

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )


engine = get_engine()


# ============================================================
# LOAD DATA FROM POSTGRESQL
# ============================================================

@st.cache_data(ttl=300)
def load_table(table_name):

    query = f'SELECT * FROM public."{table_name}"'

    try:

        return pd.read_sql(
            query,
            engine
        )

    except Exception as e:

        st.error(
            f"Could not load table `{table_name}`:\n\n{e}"
        )

        return pd.DataFrame()


# ============================================================
# DATA ONBOARDING GATE
# Ask the client to upload the raw files and run the pipeline
# BEFORE the dashboard is shown. The dashboard only renders
# once st.session_state.data_ready is True.
# ============================================================

if "data_ready" not in st.session_state:

    st.session_state.data_ready = False


def run_pipeline(sales_file, inventory_file, sku_file):

    try:

        df_sales_raw = pd.read_csv(sales_file)
        df_inventory_raw = pd.read_csv(inventory_file)
        df_sku_master = pd.read_csv(sku_file)

    except Exception as e:

        st.error(f"Could not read one of the uploaded files:\n\n{e}")

        return False

    with st.status("Running data pipeline...", expanded=True) as status:

        # ------------------------------------------------
        # 1 - CLEAN SALES
        # ------------------------------------------------

        st.write("Cleaning sales data...")

        cleaned_sales = clean_sales_data(
            df_sales_raw,
            df_sku_master
        )

        if isinstance(cleaned_sales, int):

            st.error(
                "Sales cleaning produced no usable rows. "
                "Check that sku_id values in the sales file exist "
                "in the SKU master file."
            )

            status.update(label="Pipeline failed", state="error")

            return False

        st.write(f"Cleaned sales rows: {len(cleaned_sales)}")

        # ------------------------------------------------
        # 2 - FORECAST DEMAND
        # ------------------------------------------------

        st.write("Generating demand forecast...")

        forecast_df = forecast_sales(cleaned_sales)

        if forecast_df.empty:

            st.error(
                "Forecasting produced no results. Each SKU needs at "
                "least 2 months of historical sales to forecast."
            )

            status.update(label="Pipeline failed", state="error")

            return False

        st.write(f"Forecast rows: {len(forecast_df)}")

        # ------------------------------------------------
        # 3 - CALCULATE INVENTORY RISK
        # ------------------------------------------------

        st.write("Calculating inventory risk...")

        risk_df = calculate_inventory_risk(
            df_inventory_raw,
            forecast_df
        )

        st.write(f"Risk rows: {len(risk_df)}")

        status.update(
            label="Pipeline complete",
            state="complete"
        )

    st.cache_data.clear()

    return True


if not st.session_state.data_ready:

    st.markdown("## 📦 Welcome to FORESIGHT")

    st.caption(
        "Upload your raw Sales, Inventory, and SKU master files to "
        "generate a demand forecast and inventory risk analysis."
    )

    col_sales, col_inventory, col_sku = st.columns(3)

    with col_sales:

        sales_upload = st.file_uploader(
            "Sales data (raw / dirty)",
            type=["csv"],
            key="onboard_sales"
        )

    with col_inventory:

        inventory_upload = st.file_uploader(
            "Inventory data",
            type=["csv"],
            key="onboard_inventory"
        )

    with col_sku:

        sku_upload = st.file_uploader(
            "SKU master",
            type=["csv"],
            key="onboard_sku"
        )

    st.write("")

    run_col, skip_col = st.columns([1, 1])

    with run_col:

        run_clicked = st.button(
            "🚀 Run Pipeline & Open Dashboard",
            type="primary",
            width='stretch',
            disabled=not (
                sales_upload
                and inventory_upload
                and sku_upload
            )
        )

    with skip_col:

        skip_clicked = st.button(
            "Use Existing Database Data",
            width='stretch'
        )

    if run_clicked:

        success = run_pipeline(
            sales_upload,
            inventory_upload,
            sku_upload
        )

        if success:

            st.session_state.data_ready = True

            st.rerun()

    if skip_clicked:

        st.session_state.data_ready = True

        st.rerun()

    st.stop()


# ============================================================
# LOAD PROJECT TABLES
# ============================================================

df_sales = load_table("Cleaned_sales")

df_forecast = load_table("forecasted_sales")

df_risk = load_table("inventory_risk")


# ============================================================
# BASIC DATA VALIDATION
# ============================================================

if df_risk.empty:

    st.error(
        "The `inventory_risk` table is empty or could not be loaded."
    )

    st.stop()


# ============================================================
# CLEAN COLUMN TYPES
# ============================================================

if "sku_id" in df_risk.columns:

    df_risk["sku_id"] = (
        df_risk["sku_id"]
        .astype(str)
    )


numeric_columns = [
    "Total_stock",
    "lead_time_days",
    "reorder_point",
    "Forecast_demand",
    "Coverage",
    "Coverage_Rating",
    "Stockout_Risk",
    "overstock_risk"
]

for column in numeric_columns:

    if column in df_risk.columns:

        df_risk[column] = pd.to_numeric(
            df_risk[column],
            errors="coerce"
        )


# ============================================================
# OPTIONAL SALES PREPARATION
# ============================================================

if not df_sales.empty:

    if "sale_date" in df_sales.columns:

        df_sales["sale_date"] = pd.to_datetime(
            df_sales["sale_date"],
            errors="coerce"
        )

    if "quantity" in df_sales.columns:

        df_sales["quantity"] = pd.to_numeric(
            df_sales["quantity"],
            errors="coerce"
        )

    if "revenue" in df_sales.columns:

        df_sales["revenue"] = pd.to_numeric(
            df_sales["revenue"],
            errors="coerce"
        )


# ============================================================
# OPTIONAL FORECAST PREPARATION
# ============================================================

if not df_forecast.empty:

    if "ds" in df_forecast.columns:

        df_forecast["ds"] = pd.to_datetime(
            df_forecast["ds"],
            errors="coerce"
        )

    if "yhat" in df_forecast.columns:

        df_forecast["yhat"] = pd.to_numeric(
            df_forecast["yhat"],
            errors="coerce"
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
<div>
<h1 style="margin:0; font-size:26px; font-weight:700; margin-bottom:5px;">
FORESIGHT
</h1>
<p style="font-size:12px; color:#6b7280; margin-bottom:25px;">
AI Demand &amp; Inventory Intelligence
</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("### Filters")

    # SKU filter

    sku_options = sorted(
        df_risk["sku_id"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_skus = st.multiselect(
        "SKU",
        sku_options,
        default=[]
    )

    # Action filter

    if "Action" in df_risk.columns:

        action_options = sorted(
            df_risk["Action"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_actions = st.multiselect(
            "Risk Status",
            action_options,
            default=[]
        )

    else:

        selected_actions = []

    st.divider()

    if st.button(
        "🔄 Refresh Data",
        width='stretch'
    ):

        st.cache_data.clear()

        st.rerun()

    if st.button(
        "⬆️ Upload New Data",
        width='stretch'
    ):

        st.session_state.data_ready = False

        st.rerun()


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_risk = df_risk.copy()


if selected_skus:

    filtered_risk = filtered_risk[
        filtered_risk["sku_id"].isin(
            selected_skus
        )
    ]


if selected_actions and "Action" in filtered_risk.columns:

    filtered_risk = filtered_risk[
        filtered_risk["Action"].isin(
            selected_actions
        )
    ]


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
<div>
<h1 style="margin:0; font-size:32px; font-weight:700;">
Inventory Intelligence
</h1>
<p style="margin-top:5px; color:#6b7280;">
Demand forecasting and inventory risk monitoring
</p>
</div>
<div style="padding:8px 14px; border-radius:20px; background:#10251f; color:#20d6a0; font-size:13px;">
● Database Connected
</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# ADD DATA (CSV UPLOAD)
# ============================================================

with st.expander("📥 Add Data (CSV Upload)", expanded=False):

    st.caption(
        "Upload a CSV file to append new records to the database. "
        "Column names in the file must match the target table."
    )

    tab_sales, tab_inventory, tab_sku = st.tabs(
        ["Sales", "Inventory", "SKUs"]
    )

    # --------------------------------------------------------
    # Helper to preview + insert
    # --------------------------------------------------------

    def handle_csv_upload(
        uploaded_file,
        table_name,
        expected_columns=None,
        date_columns=None,
        numeric_columns=None
    ):

        if uploaded_file is None:

            return

        try:

            new_data = pd.read_csv(uploaded_file)

        except Exception as e:

            st.error(f"Could not read CSV file:\n\n{e}")

            return

        if expected_columns:

            missing = [
                column
                for column in expected_columns
                if column not in new_data.columns
            ]

            if missing:

                st.warning(
                    f"The file is missing expected columns: {', '.join(missing)}. "
                    "You can still upload, but the data may not display correctly."
                )

        # ----------------------------------------------------
        # Coerce column types to match the database schema.
        # CSV dates/numbers often come in as mixed-format text
        # (e.g. "2026-06-22" and "17/02/2026" in the same file),
        # so parse them explicitly before inserting.
        # ----------------------------------------------------

        conversion_issues = []

        if date_columns:

            for column in date_columns:

                if column in new_data.columns:

                    parsed = pd.to_datetime(
                        new_data[column],
                        errors="coerce",
                        format="mixed",
                        dayfirst=False
                    )

                    bad_count = parsed.isna().sum() - new_data[column].isna().sum()

                    if bad_count > 0:

                        conversion_issues.append(
                            f"{bad_count} row(s) had an unreadable `{column}` value "
                            "and were set to empty."
                        )

                    new_data[column] = parsed

        if numeric_columns:

            for column in numeric_columns:

                if column in new_data.columns:

                    new_data[column] = pd.to_numeric(
                        new_data[column],
                        errors="coerce"
                    )

        if conversion_issues:

            st.warning(" ".join(conversion_issues))

        st.write(f"Preview ({len(new_data)} rows):")

        st.dataframe(
            new_data.head(10),
            width='stretch',
            hide_index=True
        )

        if st.button(
            f"Append to `{table_name}`",
            key=f"append_{table_name}"
        ):

            try:

                new_data.to_sql(
                    table_name,
                    engine,
                    schema="public",
                    if_exists="append",
                    index=False
                )

                st.success(
                    f"Added {len(new_data)} rows to `{table_name}`."
                )

                st.cache_data.clear()

                st.rerun()

            except Exception as e:

                st.error(f"Failed to insert data:\n\n{e}")

    # --------------------------------------------------------
    # Sales tab
    # --------------------------------------------------------

    with tab_sales:

        sales_file = st.file_uploader(
            "Upload sales CSV",
            type=["csv"],
            key="sales_uploader"
        )

        handle_csv_upload(
            sales_file,
            "Cleaned_sales",
            expected_columns=["sku_id", "sale_date", "quantity", "revenue"],
            date_columns=["sale_date"],
            numeric_columns=[
                "quantity",
                "unit_price",
                "discount_pct",
                "revenue",
                "shipping_days"
            ]
        )

    # --------------------------------------------------------
    # Inventory tab
    # --------------------------------------------------------

    with tab_inventory:

        inventory_file = st.file_uploader(
            "Upload inventory CSV",
            type=["csv"],
            key="inventory_uploader"
        )

        handle_csv_upload(
            inventory_file,
            "inventory_risk",
            expected_columns=[
                "sku_id",
                "Total_stock",
                "reorder_point",
                "Forecast_demand"
            ],
            numeric_columns=[
                "Total_stock",
                "lead_time_days",
                "reorder_point",
                "Forecast_demand",
                "Coverage",
                "Coverage_Rating",
                "Stockout_Risk",
                "overstock_risk"
            ]
        )

    # --------------------------------------------------------
    # SKU tab
    # --------------------------------------------------------

    with tab_sku:

        sku_file = st.file_uploader(
            "Upload SKU CSV",
            type=["csv"],
            key="sku_uploader"
        )

        handle_csv_upload(
            sku_file,
            "skus",
            expected_columns=["sku_id"]
        )


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_skus = len(filtered_risk)

total_stock = filtered_risk["Total_stock"].sum()

total_forecast = filtered_risk["Forecast_demand"].sum()


if "Stockout_Risk" in filtered_risk.columns:

    avg_stockout_risk = (
        filtered_risk["Stockout_Risk"]
        .mean()
    )

else:

    avg_stockout_risk = 0


if "Action" in filtered_risk.columns:

    critical_count = (
        filtered_risk["Action"]
        .eq("Order ASAP")
        .sum()
    )

    monitor_count = (
        filtered_risk["Action"]
        .eq("Monitor")
        .sum()
    )

    overstock_count = (
        filtered_risk["Action"]
        .eq("Overstock")
        .sum()
    )

    fine_count = (
        filtered_risk["Action"]
        .eq("Fine")
        .sum()
    )

else:

    critical_count = 0
    monitor_count = 0
    overstock_count = 0
    fine_count = 0


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(4)


with k1:

    st.metric(
        "Total SKUs",
        f"{total_skus:,}"
    )


with k2:

    st.metric(
        "Total Stock",
        f"{total_stock:,.0f}"
    )


with k3:

    st.metric(
        "Forecast Demand",
        f"{total_forecast:,.0f}"
    )


with k4:

    st.metric(
        "Avg Stockout Risk",
        f"{avg_stockout_risk:.0%}"
    )


st.markdown("---")


# ============================================================
# FORECAST CHART
# ============================================================

st.subheader("Demand Forecast")


if not df_forecast.empty and {
    "ds",
    "yhat"
}.issubset(df_forecast.columns):

    forecast_chart = df_forecast.copy()

    if selected_skus:

        forecast_chart = forecast_chart[
            forecast_chart["sku_id"].isin(
                selected_skus
            )
        ]

    daily_forecast = (
        forecast_chart
        .groupby("ds")["yhat"]
        .sum()
        .reset_index()
    )

    fig_forecast = go.Figure()

    fig_forecast.add_trace(
        go.Scatter(
            x=daily_forecast["ds"],
            y=daily_forecast["yhat"],
            mode="lines",
            name="Forecast",
            line=dict(
                width=3,
                color="#16c79a"
            ),
            fill="tozeroy",
            fillcolor="rgba(22,199,154,0.08)"
        )
    )

    # Historical sales
    #
    # forcasting.py trains Prophet on MONTHLY totals per SKU, so every
    # point in df_forecast (ds/yhat) represents a whole month's demand.
    # To compare fairly, the "Actual" line must also be aggregated to
    # monthly totals - otherwise a single day's sales gets plotted next
    # to a whole month's forecast, making the forecast look artificially
    # 20-30x bigger than actual.

    if (
        not df_sales.empty
        and "sale_date" in df_sales.columns
        and "quantity" in df_sales.columns
    ):

        sales_for_chart = df_sales.copy()

        if selected_skus:

            sales_for_chart = sales_for_chart[
                sales_for_chart["sku_id"].isin(
                    selected_skus
                )
            ]

        # Roll each sale up to the first day of its month, matching
        # the monthly "ds" timestamps produced by forcasting.py.

        sales_for_chart["sale_month"] = (
            sales_for_chart["sale_date"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        historical = (
            sales_for_chart
            .groupby("sale_month")["quantity"]
            .sum()
            .reset_index()
            .rename(columns={"sale_month": "sale_date"})
        )

        fig_forecast.add_trace(
            go.Scatter(
                x=historical["sale_date"],
                y=historical["quantity"],
                mode="lines",
                name="Actual",
                line=dict(
                    width=2,
                    color="#4c9aff"
                )
            )
        )

    fig_forecast.update_layout(
        height=360,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#6b7280"
        ),
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            gridcolor="rgba(120,140,170,0.12)"
        ),
        legend=dict(
            orientation="h",
            y=1.08
        )
    )

    st.plotly_chart(
        fig_forecast,
        use_container_width=True
    )

else:

    st.info(
        "Forecast data is not available."
    )


# ============================================================
# QUADRANT RISK MATRIX
# ============================================================

st.subheader("Inventory Risk Matrix")

st.caption(
    "Stockout risk vs. overstock risk. "
    "The four quadrants identify the recommended inventory action."
)


if {
    "Stockout_Risk",
    "overstock_risk",
    "sku_id"
}.issubset(filtered_risk.columns):

    scatter = filtered_risk.copy()

    # --------------------------------------------------------
    # Risk classification
    #
    # IMPORTANT: color by the real `Action` column (produced by
    # Risk_managment.py), not a re-derived quadrant. The previous
    # version re-classified points using only 2 axis thresholds
    # (stockout > 0.60 AND overstock > 0.60) to decide "Order ASAP",
    # but the real Action logic flags "Order ASAP" whenever
    # stockout_risk > 0.85 - regardless of overstock. That mismatch
    # is why some genuine Order ASAP SKUs were never colored red:
    # they didn't clear the chart's own (wrong) threshold. Using
    # Action directly guarantees the chart always matches the
    # Risk Summary counts below.
    # --------------------------------------------------------

    if "Action" in scatter.columns:

        color_field = "Action"

    else:

        # Fallback if Action wasn't computed for some reason.

        def classify_quadrant(row):

            stockout = row["Stockout_Risk"]
            overstock = row["overstock_risk"]

            if pd.isna(stockout) or pd.isna(overstock):

                return "Unknown"

            if stockout > 0.85:

                return "Order ASAP"

            elif stockout > 0.60:

                return "Monitor"

            elif stockout <= 0.35 and overstock > 0.60:

                return "Overstock"

            else:

                return "Fine"

        scatter["Action"] = scatter.apply(
            classify_quadrant,
            axis=1
        )

        color_field = "Action"

    # Force a fixed category order so all 4 statuses always show
    # in the legend, even if one has zero SKUs in the current filter.

    quadrant_order = [
        "Fine",
        "Monitor",
        "Overstock",
        "Order ASAP"
    ]

    quadrant_colors = {
        "Fine": "#16c79a",
        "Monitor": "#f5b642",
        "Overstock": "#4c9aff",
        "Order ASAP": "#ff3b5c"
    }


    # --------------------------------------------------------
    # Scatter plot
    # --------------------------------------------------------

    fig_risk = px.scatter(
        scatter,
        x="overstock_risk",
        y="Stockout_Risk",
        hover_name="sku_id",
        hover_data={
            "overstock_risk": ":.0%",
            "Stockout_Risk": ":.0%",
            "Total_stock": True,
            "Forecast_demand": True,
            "Coverage": ":.2f",
            color_field: True
        },
        size="Forecast_demand",
        size_max=25,
        color=color_field,
        category_orders={color_field: quadrant_order},
        color_discrete_map=quadrant_colors
    )

    # No SKU text on the markers themselves - too cluttered with
    # many points overlapping. SKU is still shown on hover.

    fig_risk.update_traces(
        mode="markers"
    )


    # --------------------------------------------------------
    # Quadrant lines
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Reference lines
    #
    # These mirror the actual thresholds used in Risk_managment.py's
    # action_from_risk(): stockout_risk 0.35 and 0.85 mark the Fine /
    # Monitor / Order ASAP bands, and overstock_risk 0.60 marks the
    # Overstock cutoff (only relevant while stockout is low).
    # --------------------------------------------------------

    fig_risk.add_vline(
        x=0.60,
        line_dash="dash",
        line_width=1,
        line_color="rgba(255,255,255,0.35)"
    )

    fig_risk.add_hline(
        y=0.35,
        line_dash="dot",
        line_width=1,
        line_color="rgba(255,255,255,0.20)"
    )

    fig_risk.add_hline(
        y=0.85,
        line_dash="dash",
        line_width=1,
        line_color="rgba(255,255,255,0.35)"
    )


    # --------------------------------------------------------
    # Quadrant labels
    # --------------------------------------------------------

    fig_risk.add_annotation(
        x=0.50,
        y=0.97,
        text="<b>ORDER ASAP</b>",
        showarrow=False,
        font=dict(
            size=13,
            color=quadrant_colors["Order ASAP"]
        )
    )

    fig_risk.add_annotation(
        x=0.50,
        y=0.72,
        text="<b>MONITOR</b>",
        showarrow=False,
        font=dict(
            size=13,
            color=quadrant_colors["Monitor"]
        )
    )

    fig_risk.add_annotation(
        x=0.85,
        y=0.17,
        text="<b>OVERSTOCK</b>",
        showarrow=False,
        font=dict(
            size=13,
            color=quadrant_colors["Overstock"]
        )
    )

    fig_risk.add_annotation(
        x=0.20,
        y=0.17,
        text="<b>FINE</b>",
        showarrow=False,
        font=dict(
            size=13,
            color=quadrant_colors["Fine"]
        )
    )


    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    fig_risk.update_layout(
        height=560,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#6b7280"
        ),
        legend_title="Recommended Action",
        xaxis=dict(
            title="Overstock Risk",
            range=[0, 1.05],
            tickformat=".0%",
            gridcolor="rgba(120,140,170,0.12)"
        ),
        yaxis=dict(
            title="Stockout Risk",
            range=[0, 1.05],
            tickformat=".0%",
            gridcolor="rgba(120,140,170,0.12)"
        )
    )


    st.plotly_chart(
        fig_risk,
        use_container_width=True
    )


# ============================================================
# RISK SUMMARY
# ============================================================

st.subheader("Risk Summary")


r1, r2, r3, r4 = st.columns(4)


with r1:

    st.metric(
        "🔴 Order ASAP",
        critical_count
    )


with r2:

    st.metric(
        "🟠 Monitor",
        monitor_count
    )


with r3:

    st.metric(
        "🟡 Overstock",
        overstock_count
    )


with r4:

    st.metric(
        "🟢 Fine",
        fine_count
    )


# ============================================================
# SKU TABLE
# ============================================================

st.subheader("SKU Intelligence")


display_columns = [
    "sku_id",
    "Total_stock",
    "reorder_point",
    "Forecast_demand",
    "Coverage",
    "Stockout_Risk",
    "overstock_risk",
    "Action"
]

display_columns = [
    column
    for column in display_columns
    if column in filtered_risk.columns
]


table = filtered_risk[
    display_columns
].copy()


# Format values

if "Coverage" in table.columns:

    table["Coverage"] = table[
        "Coverage"
    ].round(2)


if "Stockout_Risk" in table.columns:

    table["Stockout_Risk"] = (
        table["Stockout_Risk"]
        .round(2)
    )


if "overstock_risk" in table.columns:

    table["overstock_risk"] = (
        table["overstock_risk"]
        .round(2)
    )


if "Forecast_demand" in table.columns:

    table["Forecast_demand"] = (
        table["Forecast_demand"]
        .round(0)
    )


st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div style="text-align:center; color:#6b7280; font-size:12px; padding:25px 0 10px 0;">
FORESIGHT • AI-Powered Demand &amp; Inventory Intelligence
</div>
""", unsafe_allow_html=True)