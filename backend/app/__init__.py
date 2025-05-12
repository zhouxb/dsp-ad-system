from flask import Flask
from app.core.config import settings
from app.extensions import init_app as init_extensions



def create_app() -> Flask:
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(settings)
    app.config['settings'] = settings

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    from app.api.v1 import api_router
    from app.api.auth import auth_router

    app.register_blueprint(api_router, url_prefix='/api/v1')
    app.register_blueprint(auth_router, url_prefix='/auth')

    return app
