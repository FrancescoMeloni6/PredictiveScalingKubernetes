from flask import Flask, request, render_template_string
import hashlib
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter("hash_requests_total", "Total hash requests")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hash Service</title>
</head>
<body>
    <h1>Hash Generator</h1>

    <form method="post">
        <input type="text" name="input_text" placeholder="Inserisci testo">
        <button type="submit">Hash</button>
    </form>

    {% if hash_value %}
        <h3>Hash:</h3>
        <p>{{hash_value}}</p>
    {% endif %}

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def hash_service():
    hash_value = None

    if request.method == "POST":
        REQUEST_COUNT.inc()
        text = request.form.get("input_text", "")
        data = text.encode()
        data = hashlib.sha256(data).digest()
        hash_value = data.hex()

    return render_template_string(HTML_PAGE, hash_value=hash_value)

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)