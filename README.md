## FORESIGHT — AI-Powered Demand Forecasting & Inventory Intelligence Platform

**FORESIGHT** is an end-to-end AI-powered demand forecasting and inventory intelligence platform designed to help businesses make smarter, data-driven inventory decisions. The platform combines **Python, machine learning, time-series forecasting, PostgreSQL, Streamlit, and Power BI** to transform raw sales and inventory data into actionable insights.

FORESIGHT analyzes historical sales at the **SKU level**, cleans and prepares operational data, forecasts future product demand, evaluates inventory risks, and provides recommendations to help businesses maintain the right stock levels.

### 🚀 Key Capabilities

* **SKU-Level Demand Forecasting**

  * Analyzes historical sales patterns for individual SKUs.
  * Aggregates sales data at the monthly level.
  * Uses **Facebook Prophet** for time-series demand forecasting.
  * Generates forecasts for the next **3 months**.
  * Separates historical actual demand from future predicted demand.

* **Inventory Risk Analysis**

  * Identifies potential **stockout risks** caused by insufficient inventory.
  * Detects **overstock risks** that can increase inventory holding costs.
  * Evaluates inventory availability against expected future demand.
  * Produces SKU-level risk classifications to support proactive decisions.

* **Actionable Inventory Recommendations**

  * Converts forecast and inventory insights into practical recommendations.
  * Helps identify products that may require replenishment.
  * Highlights products with excessive inventory levels.
  * Supports more efficient stock planning and purchasing decisions.

* **Automated Data Pipeline**

  * Supports raw sales, inventory, and SKU master data.
  * Performs data cleaning and validation automatically.
  * Handles missing values, invalid dates, duplicates, incorrect quantities, discounts, revenue, and other data-quality issues.
  * Processes the cleaned data before forecasting and risk analysis.

* **PostgreSQL Database Integration**

  * Uses **PostgreSQL/Neon** as the central data storage layer.
  * Stores cleaned sales data, forecasts, and inventory-related analytics.
  * Provides a structured foundation for connecting the forecasting pipeline with business intelligence tools.

* **Interactive Analytics Dashboard**

  * Built with **Streamlit** for an interactive user experience.
  * Allows users to upload business data and run the analytics pipeline.
  * Provides KPI monitoring, sales analysis, demand forecasts, inventory risk analysis, and SKU-level insights.
  * Designed to make complex forecasting results accessible to business users.

* **Power BI Business Intelligence**

  * Forecasting and inventory data can be integrated with **Power BI** for advanced reporting and visualization.
  * Enables interactive dashboards for monitoring demand, inventory levels, risks, and business performance.

### 🧠 Technology Stack

```text
Python
├── Pandas
├── Prophet
├── SQLAlchemy
└── NumPy

Database
└── PostgreSQL / Neon

Visualization & BI
├── Streamlit
├── Plotly
└── Power BI

Data Processing
├── Data Cleaning
├── Time-Series Aggregation
├── SKU-Level Analysis
└── Inventory Risk Modeling
```

### 🔄 Overall Workflow

```text
Raw Sales Data
      │
      ▼
Data Cleaning & Validation
      │
      ▼
PostgreSQL Database
      │
      ├───────────────┐
      ▼               ▼
Historical Sales   Inventory Data
      │               │
      ▼               │
SKU-Level            │
Aggregation           │
      │               │
      ▼               │
Prophet Forecast      │
      │               │
      └───────┬───────┘
              ▼
      Inventory Risk Analysis
              │
              ▼
    Stockout / Overstock Detection
              │
              ▼
   Actionable Recommendations
              │
              ▼
      Streamlit / Power BI
              │
              ▼
       Business Decisions
```

### 🎯 Business Objectives

FORESIGHT is designed to help organizations:

* Improve demand visibility
* Reduce stockout incidents
* Reduce unnecessary overstock
* Optimize inventory levels
* Lower inventory holding costs
* Prevent potential lost sales
* Improve replenishment planning
* Support data-driven purchasing decisions
* Turn historical business data into actionable intelligence

### 📊 Project Outcome

By combining **machine learning-based forecasting with inventory intelligence and business intelligence**, FORESIGHT provides a complete workflow from **raw operational data → data preparation → demand prediction → inventory risk detection → actionable business insights**.

The goal is not simply to predict future sales, but to turn those predictions into **practical inventory decisions** that help businesses determine **what to stock, when to replenish, and where inventory risks are emerging**.
