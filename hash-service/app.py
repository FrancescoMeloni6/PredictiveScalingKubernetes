from flask import Flask, request, jsonify
import hashlib
from prometheus_client import Counter, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter("hash_requests_total", "Total hash requests")

@app.route("/hash", methods=["POST"])
def hash_value():
    REQUEST_COUNT.inc()

    data = request.json.get("input", "")
    result = hashlib.sha256(data.encode()).hexdigest()

    return jsonify({
        "input": data,
        "hash": result
    })

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)