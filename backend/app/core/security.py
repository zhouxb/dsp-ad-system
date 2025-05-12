import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import Flask, request, abort, g, Request
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.core.config import settings


def setup_security(app: Flask) -> None:
    """Setup security features for the Flask app"""
    # Set max content length for uploads
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
    
    # Register middleware
    app.before_request(csrf_protection)
    app.before_request(rate_limit)


def csrf_protection() -> None:
    """Check CSRF token for unsafe methods"""
    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        token = request.headers.get('X-CSRF-Token')
        if not token or not verify_csrf_token(token):
            abort(403, description="CSRF token missing or invalid")


def verify_csrf_token(token: str) -> bool:
    """Verify CSRF token"""
    try:
        # Simple HMAC verification - in a real app, this would be more sophisticated
        csrf_key = settings.CSRF_SECRET_KEY.encode()
        timestamp, signature = token.split(':', 1)
        
        # Check if token is expired (1 hour validity)
        token_time = datetime.fromtimestamp(int(timestamp))
        if datetime.now() - token_time > timedelta(hours=1):
            return False
            
        # Verify signature
        expected_sig = hmac.new(
            csrf_key, 
            f"{timestamp}:{get_jwt_identity()}".encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_sig)
    except (ValueError, TypeError):
        return False


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    timestamp = int(datetime.now().timestamp())
    signature = hmac.new(
        settings.CSRF_SECRET_KEY.encode(),
        f"{timestamp}:{get_jwt_identity()}".encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{timestamp}:{signature}"


def rate_limit() -> None:
    """Simple rate limiting middleware"""
    # This is a placeholder - a real implementation would use Redis
    # to track request counts per IP/user and time window
    pass


def encrypt_data(data: str) -> str:
    """Encrypt data using AES"""
    key = settings.AES_SECRET_KEY.encode()
    # Ensure key is 16, 24, or 32 bytes long (AES-128, AES-192, or AES-256)
    if len(key) not in (16, 24, 32):
        key = hashlib.sha256(key).digest()[:16]  # Use 16 bytes (AES-128)
    
    iv = secrets.token_bytes(16)  # Generate random IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Encrypt and combine IV with ciphertext
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted_data).decode('utf-8')


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt AES encrypted data"""
    key = settings.AES_SECRET_KEY.encode()
    if len(key) not in (16, 24, 32):
        key = hashlib.sha256(key).digest()[:16]
    
    # Decode from base64
    data = base64.b64decode(encrypted_data.encode('utf-8'))
    
    # Extract IV and ciphertext
    iv = data[:16]
    ciphertext = data[16:]
    
    # Decrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    return decrypted_data.decode('utf-8')


def create_user_token(user_id: int, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """Create JWT access token for user"""
    claims = {"user_id": user_id}
    if additional_claims:
        claims.update(additional_claims)
    
    return create_access_token(
        identity=user_id,
        additional_claims=claims,
        expires_delta=timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
    )


def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()
    return f"{salt}${pwdhash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against a provided password"""
    try:
        salt, stored_hash = hashed_password.split('$', 1)
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256', 
            plain_password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        ).hex()
        return hmac.compare_digest(pwdhash, stored_hash)
    except Exception:
        return False 