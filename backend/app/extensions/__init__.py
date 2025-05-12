from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS


# Initialize extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def init_app(app):
    """Initialize Flask extensions"""
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app) 