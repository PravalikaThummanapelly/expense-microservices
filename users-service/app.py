from flask import Flask, request, jsonify
from config import Config
from models import db, User
import jwt
import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()  # creates tables if they don't exist yet


@app.route("/health", methods=["GET"])
def health():
    # Kubernetes will call this constantly to check "is this service alive?"
    # We're adding it now so it's already there when we need it later.
    return jsonify({"status": "ok"}), 200


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "name, email and password are required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "email already registered"}), 409

    user = User(name=data["name"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"error": "invalid email or password"}), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        },
        app.config["JWT_SECRET"],
        algorithm="HS256",
    )
    return jsonify({"token": token, "user": user.to_dict()}), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # This is the internal endpoint expenses-service will call
    # to check "does this user actually exist?"
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify(user.to_dict()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
