import time
import requests
import pandas as pd
from prophet import Prophet
from datetime import datetime

PROM_URL = "http://prometheus.local"

QUERY_RANDOM = "rate(random_requests_total[30m])"
QUERY_HASH = "rate(hash_requests_total[30m])"

WINDOW_SIZE = 350
FORECAST_STEPS = 48

history_random = []
history_hash = []

def query_prometheus(query):

    r = requests.get(
        f"{PROM_URL}/api/v1/query",
        params={"query": query}
    )

    data = r.json()

    if not data["data"]["result"]:
        return 0.0

    return float(data["data"]["result"][0]["value"][1])

def add_point(history, value):

    history.append({
        "ds": datetime.now(),
        "y": value
    })

    if len(history) > WINDOW_SIZE:
        history.pop(0)

def train_model(history):

    df = pd.DataFrame(history)

    model = Prophet()

    model.fit(df)

    return model

def forecast(model, history):

    if model is None or len(history) < 10:
        return history[-1]["y"]

    future = model.make_future_dataframe(
        periods=FORECAST_STEPS,
        freq="30m"
    )

    forecast = model.predict(future)

    return forecast["yhat"].iloc[-1]

def main():

    model_random = None
    model_hash = None

    while True:

        start_time = time.time()

        random_metric = query_prometheus(QUERY_RANDOM)
        hash_metric = query_prometheus(QUERY_HASH)

        add_point(history_random, random_metric)
        add_point(history_hash, hash_metric)

        model_random = train_model(history_random)
        model_hash = train_model(history_hash)

        pred_random = forecast(model_random, history_random)
        pred_hash = forecast(model_hash, history_hash)

        print(
            "random metric:", random_metric,
            "pred:", pred_random,
        )

        print(
            "hash metric:", hash_metric,
            "pred:", pred_hash,
        )

        delta_time = start_time - time.time()

        if delta_time > 0 and delta_time < 1800:
            time.sleep(1800 - delta_time)
        else:
            time.sleep(1800)

if __name__ == "__main__":
    main()