from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load monthly sales
df = pd.read_csv(
    "C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Forcasting\\Data\\monthly_sales.csv"
)

df = df.rename(columns={
    "Month_date": "ds",
    "quantity": "y"
})


all_forecasts = []

for sku in df["sku_id"].unique():

    sku_data = df[df["sku_id"] == sku][["ds", "y"]].copy()

    sku_data = sku_data.sort_values("ds")

    model = Prophet()

    model.fit(sku_data)

    future = model.make_future_dataframe(
        periods=3,
        freq="MS"
    )

    forecast = model.predict(future)

    forecast = forecast[
        ["ds", "yhat"]
    ]

    forecast["sku_id"] = sku

    all_forecasts.append(forecast)

final_forecast = pd.concat(
    all_forecasts,
    ignore_index=True
)

final_forecast.to_csv(
    "C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Forcasting\\Data\\prophet_forecast.csv",
    index=False
)


    fig = model.plot(forecast)

    plt.title(
        f"Sales Quantity Forecast - {sku}"
    )

    plt.xlabel("Date")
    plt.ylabel("Quantity")

    plt.tight_layout()

    # Save chart
    plt.savefig(
        f"C:\\Users\\elega\\OneDrive\\Desktop\\zildio\\Forcasting\\{sku}_forecast.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

print("Forecast completed!")

print(final_forecast.head())