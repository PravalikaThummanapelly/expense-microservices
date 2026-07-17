from flask import Flask, request, jsonify
from functools import wraps
from config import Config
from models import db, Expense
import jwt
import requests

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


def require_auth(f):
    """
    Decorator that protects a route: checks for a valid JWT in the
    Authorization header before letting the request through.
    Any route wrapped with @require_auth will reject unauthenticated calls.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "invalid token"}), 401

        # Attach the verified user_id onto the request so the route can use it
        request.user_id = payload["user_id"]
        return f(*args, **kwargs)
    return wrapper


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/expenses", methods=["POST"])
@require_auth
def create_expense():
    data = request.get_json()
    if not data or "title" not in data or "amount" not in data:
        return jsonify({"error": "title and amount are required"}), 400

    expense = Expense(
        user_id=request.user_id,
        title=data["title"],
        amount=data["amount"],
        category=data.get("category", "general"),
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201


@app.route("/expenses", methods=["GET"])
@require_auth
def list_expenses():
    expenses = Expense.query.filter_by(user_id=request.user_id).all()
    return jsonify([e.to_dict() for e in expenses]), 200


@app.route("/expenses/<int:expense_id>/verify-owner", methods=["GET"])
@require_auth
def verify_owner_demo(expense_id):
    """
    Demo route showing service-to-service communication:
    calls users-service to double-check the requesting user really exists,
    instead of just trusting the JWT payload blindly.
    """
    try:
        resp = requests.get(
            f"{app.config['USERS_SERVICE_URL']}/users/{request.user_id}",
            timeout=3,
        )
    except requests.exceptions.RequestException:
        return jsonify({"error": "users-service unavailable"}), 503

    if resp.status_code != 200:
        return jsonify({"error": "user not found in users-service"}), 404

    return jsonify({
        "verified_user": resp.json(),
        "message": "confirmed via live call to users-service"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
