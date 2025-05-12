from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.models.base import db
from app.models.campaign.campaign import Campaign, Creative, TargetingRule
from app.utils.validators import validate_permissions

# Create campaign blueprint
campaign_router = Blueprint('campaign', __name__)


class CampaignSchema(Schema):
    """Schema for campaign validation"""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    advertiser_id = fields.Integer(required=True)
    daily_budget = fields.Float(required=True, validate=validate.Range(min=0.01))
    total_budget = fields.Float(required=True, validate=validate.Range(min=0.01))
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(allow_none=True)
    bid_strategy = fields.String(required=True, validate=validate.OneOf(['cpc', 'cpm', 'cpa', 'cpi']))
    bid_amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    frequency_cap = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    frequency_period = fields.String(allow_none=True, validate=validate.OneOf(['day', 'week', 'month']))
    targeting = fields.Dict(allow_none=True)
    optimization_goal = fields.String(allow_none=True)


class CampaignUpdateSchema(Schema):
    """Schema for campaign update validation"""
    name = fields.String(validate=validate.Length(min=1, max=100))
    daily_budget = fields.Float(validate=validate.Range(min=0.01))
    total_budget = fields.Float(validate=validate.Range(min=0.01))
    end_date = fields.DateTime(allow_none=True)
    bid_strategy = fields.String(validate=validate.OneOf(['cpc', 'cpm', 'cpa', 'cpi']))
    bid_amount = fields.Float(validate=validate.Range(min=0.01))
    frequency_cap = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    frequency_period = fields.String(allow_none=True, validate=validate.OneOf(['day', 'week', 'month']))
    targeting = fields.Dict(allow_none=True)
    optimization_goal = fields.String(allow_none=True)


class CampaignStatusSchema(Schema):
    """Schema for campaign status update validation"""
    status = fields.String(required=True, validate=validate.OneOf(
        ['draft', 'pending', 'active', 'paused', 'completed', 'rejected']
    ))
    reason = fields.String(validate=validate.Length(max=1000))


@campaign_router.route('/', methods=['GET'])
@jwt_required()
def get_campaigns():
    """Get list of campaigns with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Get JWT claims to check for advertiser_id
    claims = get_jwt()
    advertiser_id = claims.get('advertiser_id')
    
    # Filters
    filters = {}
    if advertiser_id and not claims.get('is_superuser'):
        # Regular users can only view their own campaigns
        filters['advertiser_id'] = advertiser_id
    
    # Query based on filters
    result = Campaign.paginate(page=page, per_page=per_page, **filters)
    
    return jsonify(result), 200


@campaign_router.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    """Get campaign details by ID"""
    # Get JWT claims to check for permissions
    claims = get_jwt()
    
    # Find campaign
    campaign = Campaign.get_by_id(campaign_id)
    if not campaign:
        return jsonify({
            "error": "Campaign not found"
        }), 404
    
    # Check permissions or ownership
    if not (claims.get('is_superuser') or 'campaigns.view' in claims.get('permissions', []) or 
            claims.get('advertiser_id') == campaign.advertiser_id):
        return jsonify({
            "error": "Not authorized to view this campaign"
        }), 403
    
    return jsonify({
        "campaign": campaign.to_dict()
    }), 200


@campaign_router.route('/', methods=['POST'])
@jwt_required()
@validate_permissions(['campaigns.create'])
def create_campaign():
    """Create a new campaign"""
    try:
        # Validate request data
        schema = CampaignSchema()
        data = schema.load(request.json)
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Create campaign
        campaign = Campaign(
            name=data['name'],
            advertiser_id=data['advertiser_id'],
            daily_budget=data['daily_budget'],
            total_budget=data['total_budget'],
            start_date=data['start_date'],
            end_date=data.get('end_date'),
            bid_strategy=data['bid_strategy'],
            bid_amount=data['bid_amount'],
            frequency_cap=data.get('frequency_cap'),
            frequency_period=data.get('frequency_period'),
            targeting=data.get('targeting'),
            optimization_goal=data.get('optimization_goal'),
            created_by_id=user_id,
            updated_by_id=user_id
        )
        
        campaign.save()
        
        return jsonify({
            "message": "Campaign created successfully",
            "campaign": campaign.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to create campaign: {str(e)}"
        }), 500


@campaign_router.route('/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    """Update an existing campaign"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()
        
        # Find campaign
        campaign = Campaign.get_by_id(campaign_id)
        if not campaign:
            return jsonify({
                "error": "Campaign not found"
            }), 404
        
        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'campaigns.update' in claims.get('permissions', []) or 
                claims.get('advertiser_id') == campaign.advertiser_id):
            return jsonify({
                "error": "Not authorized to update this campaign"
            }), 403
        
        # Validate request data
        schema = CampaignUpdateSchema()
        data = schema.load(request.json)
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Update allowed fields
        for field in data:
            setattr(campaign, field, data[field])
            
        # Update audit fields
        campaign.updated_by_id = user_id
        
        # Log change in audit log
        campaign.log_change(user_id, "update", data)
        
        # Save changes
        campaign.save()
        
        return jsonify({
            "message": "Campaign updated successfully",
            "campaign": campaign.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update campaign: {str(e)}"
        }), 500


@campaign_router.route('/<int:campaign_id>/status', methods=['PUT'])
@jwt_required()
@validate_permissions(['campaigns.review'])
def update_campaign_status(campaign_id):
    """Update campaign status"""
    try:
        # Find campaign
        campaign = Campaign.get_by_id(campaign_id)
        if not campaign:
            return jsonify({
                "error": "Campaign not found"
            }), 404
        
        # Validate request data
        schema = CampaignStatusSchema()
        data = schema.load(request.json)
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Update status
        campaign.status = data['status']
        if data.get('reason'):
            campaign.rejection_reason = data['reason']
            
        # Update audit fields
        campaign.updated_by_id = user_id
        
        # Log change in audit log
        campaign.log_change(user_id, "status_change", data)
        
        # Save changes
        campaign.save()
        
        return jsonify({
            "message": f"Campaign status updated to {data['status']}",
            "campaign": campaign.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update campaign status: {str(e)}"
        }), 500


@campaign_router.route('/<int:campaign_id>/targeting', methods=['PUT'])
@jwt_required()
def update_campaign_targeting(campaign_id):
    """Update campaign targeting rules"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()
        
        # Find campaign
        campaign = Campaign.get_by_id(campaign_id)
        if not campaign:
            return jsonify({
                "error": "Campaign not found"
            }), 404
        
        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'campaigns.update' in claims.get('permissions', []) or 
                claims.get('advertiser_id') == campaign.advertiser_id):
            return jsonify({
                "error": "Not authorized to update this campaign"
            }), 403
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Update targeting
        targeting_data = request.json
        campaign.set_targeting(targeting_data)
        
        # Update audit fields
        campaign.updated_by_id = user_id
        
        # Log change in audit log
        campaign.log_change(user_id, "targeting_update", targeting_data)
        
        # Save changes
        campaign.save()
        
        return jsonify({
            "message": "Campaign targeting updated successfully",
            "campaign": campaign.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to update campaign targeting: {str(e)}"
        }), 500 