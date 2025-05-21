from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
# from celery import Celery
from neo4j import GraphDatabase
from app.core.config import settings
from flask import request, make_response

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
# celery = Celery()
neo4j_driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
)

def init_app(app):
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    # celery.init_app(app)

    cors.init_app(app, supports_credentials=True, origins=app.config.get('CORS_ORIGINS', []))
    # Configure CORS
    """
    @app.after_request
    def after_request(response):
        print("Request headers:", dict(request.headers))
        origin = request.headers.get('Origin')
        if origin in settings.CORS_ORIGINS:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRF-Token')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Expose-Headers', 'Content-Type,X-CSRF-Token')
        return response

    @app.before_request
    def handle_preflight():
        print("Request method:", request.method)
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin'))
            response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-CSRF-Token")
            response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            response.headers.add("Access-Control-Max-Age", "3600")
            return response
    """
