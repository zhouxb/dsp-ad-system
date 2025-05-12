import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.api.v1 import api_router
from app.api.auth import auth_router
from app.core.config import settings
from app.core.security import setup_security
from app.models.base import db, migrate



def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_object(settings)

    # Load test configuration if provided
    if test_config:
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize JWT
    jwt = JWTManager(app)

    # Setup security features
    setup_security(app)

    # Setup CORS
    CORS(app, resources={r"/api/*": {"origins": settings.CORS_ORIGINS}})

    # Register blueprints
    app.register_blueprint(api_router, url_prefix='/api/v1')
    app.register_blueprint(auth_router, url_prefix='/api/auth')

    @app.route('/health')
    def health_check():
        return {"status": "healthy", "version": settings.API_VERSION}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=7000, debug=settings.DEBUG)


