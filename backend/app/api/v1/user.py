from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

from app.models.base import db
from app.models.user.user import User, Role, Permission
from app.utils.validators import validate_permissions
from app.utils.email import send_password_reset_email, send_welcome_email

# Create user blueprint
user_router = Blueprint('user', __name__)


class UserSchema(Schema):
    """Schema for user validation"""
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    role_id = fields.Integer(required=True)
    advertiser_id = fields.Integer(allow_none=True)
    is_active = fields.Boolean(default=True)


class UserUpdateSchema(Schema):
    """Schema for user update validation"""
    first_name = fields.String(validate=validate.Length(min=1, max=50))
    last_name = fields.String(validate=validate.Length(min=1, max=50))
    role_id = fields.Integer()
    advertiser_id = fields.Integer(allow_none=True)
    is_active = fields.Boolean()


class PasswordUpdateSchema(Schema):
    """Schema for password update validation"""
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))


class PasswordResetRequestSchema(Schema):
    """Schema for password reset request validation"""
    email = fields.Email(required=True)


class PasswordResetSchema(Schema):
    """Schema for password reset validation"""
    token = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))


@user_router.route('/register', methods=['POST'])
@jwt_required()
@validate_permissions(['users.create'])
def register_user():
    """Register a new user"""
    try:
        # Validate request data
        schema = UserSchema()
        data = schema.load(request.json)
        
        # Check if email already exists
        if User.get_by_email(data['email']):
            return jsonify({
                "error": "Email already registered"
            }), 400
            
        # Get current user for audit
        current_user_id = get_jwt_identity()
        
        # Create user
        user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role_id=data['role_id'],
            advertiser_id=data.get('advertiser_id'),
            is_active=data.get('is_active', True),
            created_by_id=current_user_id,
            updated_by_id=current_user_id
        )
        
        # Save user
        user.save()
        
        # Send welcome email
        send_welcome_email(user)
        
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to register user: {str(e)}"
        }), 500


@user_router.route('/', methods=['GET'])
@jwt_required()
@validate_permissions(['users.view'])
def get_users():
    """Get list of users with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Get JWT claims to check for advertiser_id
    claims = get_jwt()
    advertiser_id = claims.get('advertiser_id')
    
    # Filters
    filters = {}
    if advertiser_id and not claims.get('is_superuser'):
        # Regular users can only view users from their advertiser
        filters['advertiser_id'] = advertiser_id
    
    # Query based on filters
    result = User.paginate(page=page, per_page=per_page, **filters)
    
    return jsonify(result), 200


@user_router.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    # Get JWT claims to check for permissions
    claims = get_jwt()
    
    # Find user
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            "error": "User not found"
        }), 404
    
    # Check permissions or ownership
    if not (claims.get('is_superuser') or 'users.view' in claims.get('permissions', []) or 
            claims.get('advertiser_id') == user.advertiser_id or 
            claims.get('sub') == user_id):
        return jsonify({
            "error": "Not authorized to view this user"
        }), 403
    
    return jsonify({
        "user": user.to_dict()
    }), 200


@user_router.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user details"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()
        
        # Find user
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                "error": "User not found"
            }), 404
        
        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'users.update' in claims.get('permissions', []) or 
                claims.get('advertiser_id') == user.advertiser_id or 
                claims.get('sub') == user_id):
            return jsonify({
                "error": "Not authorized to update this user"
            }), 403
        
        # Validate request data
        schema = UserUpdateSchema()
        data = schema.load(request.json)
        
        # Get current user for audit
        current_user_id = get_jwt_identity()
        
        # Update allowed fields
        for field in data:
            setattr(user, field, data[field])
            
        # Update audit fields
        user.updated_by_id = current_user_id
        
        # Log change in audit log
        user.log_change(current_user_id, "update", data)
        
        # Save changes
        user.save()
        
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update user: {str(e)}"
        }), 500


@user_router.route('/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def update_password(user_id):
    """Update user password"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()
        
        # Find user
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                "error": "User not found"
            }), 404
        
        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'users.update' in claims.get('permissions', []) or 
                claims.get('sub') == user_id):
            return jsonify({
                "error": "Not authorized to update this user's password"
            }), 403
        
        # Validate request data
        schema = PasswordUpdateSchema()
        data = schema.load(request.json)
        
        # Verify current password
        if not check_password_hash(user.password, data['current_password']):
            return jsonify({
                "error": "Current password is incorrect"
            }), 400
        
        # Get current user for audit
        current_user_id = get_jwt_identity()
        
        # Update password
        user.password = generate_password_hash(data['new_password'])
        user.updated_by_id = current_user_id
        
        # Log change in audit log
        user.log_change(current_user_id, "password_update")
        
        # Save changes
        user.save()
        
        return jsonify({
            "message": "Password updated successfully"
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update password: {str(e)}"
        }), 500


@user_router.route('/password/reset-request', methods=['POST'])
def request_password_reset():
    """Request password reset"""
    try:
        # Validate request data
        schema = PasswordResetRequestSchema()
        data = schema.load(request.json)
        
        # Find user
        user = User.get_by_email(data['email'])
        if not user:
            return jsonify({
                "error": "Email not found"
            }), 404
        
        # Generate reset token
        token = user.generate_reset_token()
        
        # Send reset email
        send_password_reset_email(user, token)
        
        return jsonify({
            "message": "Password reset instructions sent to your email"
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to request password reset: {str(e)}"
        }), 500


@user_router.route('/password/reset', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        # Validate request data
        schema = PasswordResetSchema()
        data = schema.load(request.json)
        
        # Verify token and get user
        user = User.verify_reset_token(data['token'])
        if not user:
            return jsonify({
                "error": "Invalid or expired token"
            }), 400
        
        # Update password
        user.password = generate_password_hash(data['new_password'])
        user.updated_by_id = user.id  # Self-update
        
        # Log change in audit log
        user.log_change(user.id, "password_reset")
        
        # Save changes
        user.save()
        
        return jsonify({
            "message": "Password reset successfully"
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to reset password: {str(e)}"
        }), 500


@user_router.route('/roles', methods=['GET'])
@jwt_required()
@validate_permissions(['roles.view'])
def get_roles():
    """Get list of roles"""
    roles = Role.query.all()
    return jsonify({
        "roles": [role.to_dict() for role in roles]
    }), 200


@user_router.route('/permissions', methods=['GET'])
@jwt_required()
@validate_permissions(['permissions.view'])
def get_permissions():
    """Get list of permissions"""
    permissions = Permission.query.all()
    return jsonify({
        "permissions": [permission.to_dict() for permission in permissions]
    }), 200 