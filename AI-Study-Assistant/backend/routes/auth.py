from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from extensions import db
from models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "Request body is required."
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name:
        return jsonify({
            "detail": "Name is required."
        }), 400

    if not email:
        return jsonify({
            "detail": "Email is required."
        }), 400

    if not password:
        return jsonify({
            "detail": "Password is required."
        }), 400

    if len(password) < 6:
        return jsonify({
            "detail": "Password must contain at least 6 characters."
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:

        return jsonify({
            "detail": "User with this email already exists."
        }), 409

    user = User(
        name=name,
        email=email
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful.",
        "user": user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:

        return jsonify({
            "detail": "Request body is required."
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:

        return jsonify({
            "detail": "Email and password are required."
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user or not user.check_password(password):

        return jsonify({
            "detail": "Invalid email or password."
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Login successful.",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def current_user():

    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    if not user:

        return jsonify({
            "detail": "User not found."
        }), 404

    return jsonify({
        "user": user.to_dict()
    }), 200