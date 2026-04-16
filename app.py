from flask import Flask, render_template

from uplink_model import build_dashboard_payload


app = Flask(__name__)


@app.route("/")
def index():
    payload = build_dashboard_payload()
    return render_template("index.html", payload=payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)