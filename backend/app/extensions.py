from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()

def init_app(app):
    """Initialize Flask extensions"""
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    
    # 配置 JWT
    app.config['JWT_SECRET_KEY'] = app.config['settings'].JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = app.config['settings'].JWT_ACCESS_TOKEN_EXPIRES
    jwt.init_app(app)