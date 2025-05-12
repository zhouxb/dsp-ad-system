from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError
import os
import uuid
from werkzeug.utils import secure_filename

from app.models.base import db
from app.models.campaign.campaign import Creative, Campaign
from app.utils.validators import validate_permissions

# Create creative blueprint
creative_router = Blueprint('creative', __name__)


class CreativeSchema(Schema):
    """Schema for creative validation"""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    campaign_id = fields.Integer(required=True)
    creative_type = fields.String(required=True, validate=validate.OneOf(['banner', 'video', 'native', 'text']))
    landing_url = fields.String(required=True, validate=validate.URL())
    width = fields.Integer(allow_none=True)
    height = fields.Integer(allow_none=True)
    duration = fields.Integer(allow_none=True)
    weight = fields.Integer(default=100)
    content = fields.Dict(allow_none=True)


class CreativeUpdateSchema(Schema):
    """Schema for creative update validation"""
    name = fields.String(validate=validate.Length(min=1, max=100))
    landing_url = fields.String(validate=validate.URL())
    weight = fields.Integer(validate=validate.Range(min=1, max=1000))
    content = fields.Dict(allow_none=True)


class CreativeStatusSchema(Schema):
    """Schema for creative status update validation"""
    status = fields.String(required=True, validate=validate.OneOf(
        ['draft', 'pending', 'active', 'paused', 'rejected']
    ))
    reason = fields.String(validate=validate.Length(max=1000))


@creative_router.route('/', methods=['GET'])
@jwt_required()
def get_creatives():
    """Get list of creatives with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Get JWT claims to check for advertiser_id
    claims = get_jwt()
    advertiser_id = claims.get('advertiser_id')
    
    # Filters
    filters = {}
    if advertiser_id and not claims.get('is_superuser'):
        # Regular users can only view their own creatives
        filters['advertiser_id'] = advertiser_id
    
    # Query based on filters
    result = Creative.paginate(page=page, per_page=per_page, **filters)
    
    return jsonify(result), 200


@creative_router.route('/<int:creative_id>', methods=['GET'])
@jwt_required()
def get_creative(creative_id):
    """Get creative details by ID"""
    # Get JWT claims to check for permissions
    claims = get_jwt()
    
    # Find creative
    creative = Creative.get_by_id(creative_id)
    if not creative:
        return jsonify({
            "error": "Creative not found"
        }), 404
    
    # Check permissions or ownership
    if not (claims.get('is_superuser') or 'creatives.view' in claims.get('permissions', []) or 
            claims.get('advertiser_id') == creative.campaign.advertiser_id):
        return jsonify({
            "error": "Not authorized to view this creative"
        }), 403
    
    return jsonify({
        "creative": creative.to_dict()
    }), 200


@creative_router.route('/', methods=['POST'])
@jwt_required()
@validate_permissions(['creatives.create'])
def create_creative():
    """Create a new creative"""
    try:
        # Validate request data
        schema = CreativeSchema()
        data = schema.load(request.json)
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Create creative
        creative = Creative(
            name=data['name'],
            campaign_id=data['campaign_id'],
            creative_type=data['creative_type'],
            landing_url=data['landing_url'],
            width=data.get('width'),
            height=data.get('height'),
            duration=data.get('duration'),
            weight=data.get('weight', 100),
            content=data.get('content'),
            created_by_id=user_id,
            updated_by_id=user_id
        )
        
        creative.save()
        
        return jsonify({
            "message": "Creative created successfully",
            "creative": creative.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to create creative: {str(e)}"
        }), 500


@creative_router.route('/<int:creative_id>', methods=['PUT'])
@jwt_required()
def update_creative(creative_id):
    """Update an existing creative"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()
        
        # Find creative
        creative = Creative.get_by_id(creative_id)
        if not creative:
            return jsonify({
                "error": "Creative not found"
            }), 404
        
        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'creatives.update' in claims.get('permissions', []) or 
                claims.get('advertiser_id') == creative.campaign.advertiser_id):
            return jsonify({
                "error": "Not authorized to update this creative"
            }), 403
        
        # Validate request data
        schema = CreativeUpdateSchema()
        data = schema.load(request.json)
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Update allowed fields
        for field in data:
            setattr(creative, field, data[field])
            
        # Update audit fields
        creative.updated_by_id = user_id
        
        # Log change in audit log
        creative.log_change(user_id, "update", data)
        
        # Save changes
        creative.save()
        
        return jsonify({
            "message": "Creative updated successfully",
            "creative": creative.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update creative: {str(e)}"
        }), 500


@creative_router.route('/<int:creative_id>/status', methods=['PUT'])
@jwt_required()
@validate_permissions(['creatives.review'])
def update_creative_status(creative_id):
    """Update creative status"""
    try:
        # Find creative
        creative = Creative.get_by_id(creative_id)
        if not creative:
            return jsonify({
                "error": "Creative not found"
            }), 404
        
        # Validate request data
        schema = CreativeStatusSchema()
        data = schema.load(request.json)
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Update status
        creative.status = data['status']
        if data.get('reason'):
            creative.rejection_reason = data['reason']
            
        # Update audit fields
        creative.updated_by_id = user_id
        
        # Log change in audit log
        creative.log_change(user_id, "status_change", data)
        
        # Save changes
        creative.save()
        
        return jsonify({
            "message": f"Creative status updated to {data['status']}",
            "creative": creative.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update creative status: {str(e)}"
        }), 500


@creative_router.route('/<int:creative_id>/upload', methods=['POST'])
@jwt_required()
def upload_creative_file(creative_id):
    """Upload creative content file"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()
        
        # Find creative
        creative = Creative.get_by_id(creative_id)
        if not creative:
            return jsonify({
                "error": "Creative not found"
            }), 404
        
        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'creatives.update' in claims.get('permissions', []) or 
                claims.get('advertiser_id') == creative.campaign.advertiser_id):
            return jsonify({
                "error": "Not authorized to upload files for this creative"
            }), 403
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided"
            }), 400
            
        file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({
                "error": "Empty file provided"
            }), 400
            
        # Check if file type is allowed
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                "error": f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            }), 400
            
        # Secure filename and create unique name
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Create upload directory if not exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'creatives', str(creative_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Get current user for audit
        user_id = get_jwt_identity()
        
        # Update creative content URL
        content_url = os.path.join('creatives', str(creative_id), unique_filename)
        creative.content_url = content_url
        creative.updated_by_id = user_id
        
        # Log change in audit log
        creative.log_change(user_id, "file_upload", {
            "filename": filename,
            "content_url": content_url
        })
        
        # Save changes
        creative.save()
        
        return jsonify({
            "message": "File uploaded successfully",
            "creative": creative.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to upload file: {str(e)}"
        }), 500 