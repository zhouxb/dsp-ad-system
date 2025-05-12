from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt

def validate_permissions(required_permissions):
    """
    Decorator to validate if user has required permissions
    
    Args:
        required_permissions: List of permission strings required
        
    Returns:
        Decorated function if user has permission, 403 response otherwise
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get current user permissions from JWT
            claims = get_jwt()
            user_permissions = claims.get('permissions', [])
            is_superuser = claims.get('is_superuser', False)
            
            # Superusers have all permissions
            if is_superuser:
                return fn(*args, **kwargs)
                
            # Check if user has any of the required permissions
            has_permission = False
            for permission in required_permissions:
                if permission in user_permissions or '*' in user_permissions:
                    has_permission = True
                    break
                    
            if not has_permission:
                return jsonify({
                    "error": "Not authorized to perform this action",
                    "required_permissions": required_permissions
                }), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def validate_json_content_type(fn):
    """
    Decorator to validate that request has JSON content type
    
    Returns:
        Decorated function if content type is JSON, 415 response otherwise
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 415
        return fn(*args, **kwargs)
    return wrapper


def validate_rate_limit(limit_key, rate_limit="100/hour"):
    """
    Decorator to apply rate limiting based on a key
    
    Args:
        limit_key: Function that returns the key to rate limit on (e.g., IP, user ID)
        rate_limit: Rate limit string in format "number/period" 
                    (e.g., "100/hour", "1000/day")
    
    Returns:
        Decorated function if under rate limit, 429 response otherwise
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get key to rate limit on
            if callable(limit_key):
                key = limit_key()
            else:
                key = limit_key
                
            # TODO: Implement actual rate limiting with Redis
            # This is a placeholder for now
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator 