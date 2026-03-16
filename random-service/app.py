from flask import Flask, render_template_string
import random
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter("random_requests_total", "Total random number requests")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Random Number Service</title>
</head>
<body>
    <h1>Random Number Generator</h1>
    <h2>{{number}}</h2>
    <form method="get">
        <button type="submit">Genera</button>
    </form>
</body>
</html>
"""

@app.route("/")
def random_number():
    REQUEST_COUNT.inc()
    r = random.randint(0, 1000000)
    value = 0
    for _ in range(r): # simulazione lavoro CPU
        value += 1
    return render_template_string(HTML_PAGE, number=value)

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)