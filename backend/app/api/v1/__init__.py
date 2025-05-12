from flask import Blueprint
from app.api.v1.advertiser import advertiser_router
from app.api.v1.campaign import campaign_router
from app.api.v1.creative import creative_router
from app.api.v1.report import report_router
from app.api.v1.user import user_router

# Create API v1 blueprint
api_router = Blueprint('api_v1', __name__)

# Register sub-routers
api_router.register_blueprint(advertiser_router, url_prefix='/advertisers')
api_router.register_blueprint(campaign_router, url_prefix='/campaigns')
api_router.register_blueprint(creative_router, url_prefix='/creatives')
api_router.register_blueprint(report_router, url_prefix='/reports')
api_router.register_blueprint(user_router, url_prefix='/users')
