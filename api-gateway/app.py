from flask import Flask, request, jsonify, Response
from config import Config
import requests

app = Flask(__name__)
app.config.from_object(Config)


def proxy_request(target_base_url, path):
    """
    Forwards the incoming request to a backend service and relays its
    response back untouched. This one function is the entire gateway.
    """
    url = f"{target_base_url}/{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers if k.lower() != "host"},
            json=request.get_json(silent=True),
            params=request.args,
            timeout=5,
        )
    except requests.exceptions.RequestException:
        return jsonify({"error": f"upstream service unavailable: {target_base_url}"}), 503

    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "api-gateway"}), 200


# Anything hitting /auth/... gets forwarded to users-service
# e.g. POST /auth/signup -> POST http://users-service/signup
@app.route("/auth/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def auth_proxy(path):
    return proxy_request(app.config["USERS_SERVICE_URL"], path)


# Anything hitting /expenses/... gets forwarded to expenses-service.
# expenses-service's own routes are /expenses and /expenses/<id>/..., so we
# must preserve the "expenses" prefix when rebuilding the upstream URL.
@app.route("/expenses", defaults={"subpath": ""}, methods=["GET", "POST"])
@app.route("/expenses/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
def expenses_proxy(subpath):
    path = f"expenses/{subpath}" if subpath else "expenses"
    return proxy_request(app.config["EXPENSES_SERVICE_URL"], path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
