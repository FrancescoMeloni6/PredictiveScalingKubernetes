from flask import Flask, jsonify
import random
from prometheus_client import Counter, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter("random_requests_total", "Total random number requests")

@app.route("/random")
def random_number():
    REQUEST_COUNT.inc()
    value = random.randint(0, 1000000)
    return jsonify({"value": value})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)