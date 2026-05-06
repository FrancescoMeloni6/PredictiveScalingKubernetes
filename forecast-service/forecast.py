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
PRED_HASH   = Gauge("predicted_hash_rate",   "Predicted hash req/sec")

PROM_URL     = "http://prometheus-server.default.svc:80"
QUERY_RANDOM = "sum(rate(random_requests_total[5m]))"
QUERY_HASH   = "sum(rate(hash_requests_total[5m]))"

WINDOW_SIZE    = 2500
FORECAST_STEPS = 1

history_random = []
history_hash   = []

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

def query_prometheus(query):
    r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": query})
    data = r.json()
    if not data["data"]["result"]:
        return 0.0
    return float(data["data"]["result"][0]["value"][1])

def add_point(history, value):
    history.append({"ds": datetime.now(), "y": value})
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
    if model is None or len(history) < 288:
        # return history[-1]["y"]
        return 0.5 # usato nella simulazione per far vedere quando il modello inizia veramente a funzionare

    future = model.make_future_dataframe(periods=FORECAST_STEPS, freq="5min")
    pred   = model.predict(future)

    return max(pred["yhat_upper"].iloc[-1], 0.0)

def loop():
    while True:
        start_time = time.time()

        random_metric = query_prometheus(QUERY_RANDOM)
        hash_metric   = query_prometheus(QUERY_HASH)

        add_point(history_random, random_metric)
        add_point(history_hash,   hash_metric)

        model_random = train_model(history_random)
        model_hash   = train_model(history_hash)

        pred_random = forecast(model_random, history_random)
        pred_hash   = forecast(model_hash,   history_hash)

        PRED_RANDOM.set(pred_random)
        PRED_HASH.set(pred_hash)

        elapsed = time.time() - start_time
        time.sleep(max(0, 300 - elapsed))

if __name__ == "__main__":
    threading.Thread(target=loop).start()
    app.run(host="0.0.0.0", port=8000)