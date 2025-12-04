from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

RELAY_KEY = os.getenv("RELAY_ACCESS_KEY")

@app.route("/vt")
def vt():
    client_key = request.headers.get("X-Relay-Auth")

    if client_key != RELAY_KEY:
        return jsonify({"error": "forbidden"}), 403

    vt_key = request.headers.get("X-VT-Key")
    if not vt_key:
        return jsonify({"error": "missing VT key"}), 400

    domain = request.args.get("domain")
    if not domain:
        return jsonify({"error": "missing domain"}), 400

    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": vt_key}

    try:
        r = requests.get(url, headers=headers)
        return jsonify(r.json())
    except Exception as e:
        print(e)
        return jsonify({"error": "proxy_error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
