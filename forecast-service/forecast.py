import time
import requests
import threading
import pandas as pd
from prophet import Prophet
from datetime import datetime
from flask import Flask
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

PRED_RANDOM = Gauge("predicted_random_rate", "Predicted random req/sec")
PRED_HASH = Gauge("predicted_hash_rate", "Predicted hash req/sec")

PROM_URL = "http://prometheus-server.default.svc:80"

QUERY_RANDOM = "sum(rate(random_requests_total[30m]))"
QUERY_HASH = "sum(rate(hash_requests_total[30m]))"

WINDOW_SIZE = 350
FORECAST_STEPS = 48

history_random = []
history_hash = []

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

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

    if len(history) < 10:
        return None
    
    df = pd.DataFrame(history)

    model = Prophet()

    model.fit(df)

    return model

def forecast(model, history):

    if model is None or len(history) < 10:
        return history[-1]["y"]

    future = model.make_future_dataframe(
        periods=FORECAST_STEPS,
        freq="5m"
    )

    forecast = model.predict(future)

    return forecast["yhat"].iloc[-1]

def loop():

    model_random = None
    model_hash = None

    iterations = 0

    while True:
        print("iterations:", iterations)
        start_time = time.time()

        random_metric = query_prometheus(QUERY_RANDOM)
        hash_metric = query_prometheus(QUERY_HASH)

        add_point(history_random, random_metric)
        add_point(history_hash, hash_metric)

        if iterations % 5 == 0:
            model_random = train_model(history_random)
            model_hash = train_model(history_hash)
        
        iterations += 1

        pred_random = forecast(model_random, history_random)
        pred_hash = forecast(model_hash, history_hash)

        PRED_RANDOM.set(pred_random)
        PRED_HASH.set(pred_hash)

        print(
            "random metric:", random_metric,
            "pred:", pred_random,
        )

        print(
            "hash metric:", hash_metric,
            "pred:", pred_hash,
        )

        delta_time = time.time() - start_time

        if delta_time < 0 :
            print("delta time < 0")
            time.sleep(300)
        elif delta_time < 300:
            print("delta time < 300 delta_time:", delta_time)
            time.sleep(300 - delta_time)


if __name__ == "__main__":
    threading.Thread(target=loop).start()
    app.run(host="0.0.0.0", port=8000)