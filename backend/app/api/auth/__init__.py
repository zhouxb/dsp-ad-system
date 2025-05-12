from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.models.user.user import User
from app.core.security import generate_csrf_token

# Create auth blueprint
auth_router = Blueprint('auth', __name__)


class LoginSchema(Schema):
    """Schema for login validation"""
    username = fields.String(required=True)
    password = fields.String(required=True)


@auth_router.route('/login', methods=['POST'])
@jwt_required(optional=True)
def login():
    """Authenticate user and return JWT token"""

    print('here login ...')
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.json)

        print(request.json)
        print(data)

        # Check credentials
        user = User.get_by_username(data['username'])

        print('user', user)

        if not user or not user.check_password(data['password']):
            return jsonify({
                "error": "Invalid credentials"
            }), 401

        if not user.is_active:
            return jsonify({
                "error": "User account is inactive"
            }), 403

        # Create access token
        additional_claims = {
            "permissions": user.get_permissions(),
            "is_superuser": user.is_superuser
        }

        if user.advertiser_id:
            additional_claims["advertiser_id"] = user.advertiser_id

        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )

        # Generate CSRF token for protected requests
        csrf_token = generate_csrf_token()

        # Update last login
        user.last_login = datetime.utcnow()
        user.save()

        return jsonify({
            "access_token": access_token,
            "csrf_token": csrf_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_superuser": user.is_superuser,
                "advertiser_id": user.advertiser_id
            }
        }), 200

    except ValidationError as e:
        print('ValidationError', e)
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        print('Exception', e)
        return jsonify({
            "error": f"Login failed: {str(e)}"
        }), 500


@auth_router.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token is valid and return user info"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    if not user.is_active:
        return jsonify({
            "error": "User account is inactive"
        }), 403

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
            "advertiser_id": user.advertiser_id
        }
    }), 200


@auth_router.route('/csrf-token', methods=['GET'])
@jwt_required()
def refresh_csrf_token():
    """Generate a new CSRF token"""
    csrf_token = generate_csrf_token()
    return jsonify({
        "csrf_token": csrf_token
    }), 200
