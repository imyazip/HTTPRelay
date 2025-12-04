from flask import Flask, request, Response, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

RELAY_KEY = os.getenv("RELAY_ACCESS_KEY")

HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade"
}


@app.route("/proxy", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy():
    client_key = request.headers.get("X-Relay-Auth")
    if client_key != RELAY_KEY:
        return jsonify({"error": "forbidden"}), 403

    target_url = request.args.get("url")
    if not target_url:
        return jsonify({"error": "missing ?url="}), 400
    
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
        and k.lower() != "host"
    }

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=30
        )

        excluded_resp_headers = HOP_BY_HOP_HEADERS | {"content-encoding", "content-length"}
        response_headers = [
            (name, value)
            for name, value in resp.raw.headers.items()
            if name.lower() not in excluded_resp_headers
        ]

        return Response(
            resp.content,
            status=resp.status_code,
            headers=response_headers
        )

    except Exception as e:
        print("Proxy error:", e)
        return jsonify({"error": "proxy_exception"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
