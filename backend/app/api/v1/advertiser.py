from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError
import os
import uuid
from werkzeug.utils import secure_filename

from app.models.base import db
from app.models.advertiser.advertiser import Advertiser, QualificationFile, Transaction
from app.models.user.user import User
from app.utils.validators import validate_permissions

# Create advertiser blueprint
advertiser_router = Blueprint('advertiser', __name__)


class AdvertiserSchema(Schema):
    """Schema for advertiser validation"""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    company_name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    credit_code = fields.String(required=False, validate=validate.Length(max=50))
    contact_person = fields.String(required=True, validate=validate.Length(min=1, max=50))
    contact_phone = fields.String(required=True, validate=validate.Length(min=1, max=20))
    contact_email = fields.String(required=True, validate=validate.Email())
    address = fields.String(required=False, validate=validate.Length(max=255))
    industry = fields.String(required=False, validate=validate.Length(max=50))
    business_type = fields.String(required=False, validate=validate.Length(max=50))


class AdvertiserUpdateSchema(Schema):
    """Schema for advertiser update validation"""
    name = fields.String(validate=validate.Length(min=1, max=100))
    contact_person = fields.String(validate=validate.Length(min=1, max=50))
    contact_phone = fields.String(validate=validate.Length(min=1, max=20))
    contact_email = fields.String(validate=validate.Email())
    address = fields.String(validate=validate.Length(max=255))
    industry = fields.String(validate=validate.Length(max=50))
    business_type = fields.String(validate=validate.Length(max=50))


class AdvertiserStatusSchema(Schema):
    """Schema for advertiser status update validation"""
    status = fields.String(required=True, validate=validate.OneOf(
        ['pending', 'approved', 'rejected', 'suspended']
    ))
    reason = fields.String(validate=validate.Length(max=1000))


class TransactionSchema(Schema):
    """Schema for transaction validation"""
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    transaction_id = fields.String(required=True)
    details = fields.Dict(required=False)


@advertiser_router.route('/', methods=['GET'])
@jwt_required()
@validate_permissions(['advertisers.view'])
def get_advertisers():
    """Get list of advertisers with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # Get JWT claims to check for advertiser_id
    claims = get_jwt()
    advertiser_id = claims.get('advertiser_id')

    # Filters
    filters = {}
    if advertiser_id and not claims.get('is_superuser'):
        # Regular users can only view their own advertiser
        filters['id'] = advertiser_id

    # Query based on filters
    result = Advertiser.paginate(page=page, per_page=per_page, **filters)

    return jsonify(result), 200


@advertiser_router.route('/<int:advertiser_id>', methods=['GET'])
@jwt_required()
def get_advertiser(advertiser_id):
    """Get advertiser details by ID"""
    # Get JWT claims to check for permissions
    claims = get_jwt()

    # Check permissions or ownership
    if not (claims.get('is_superuser') or 'advertisers.view' in claims.get('permissions', []) or
            claims.get('advertiser_id') == advertiser_id):
        return jsonify({
            "error": "Not authorized to view this advertiser"
        }), 403

    advertiser = Advertiser.get_by_id(advertiser_id)
    if not advertiser:
        return jsonify({
            "error": "Advertiser not found"
        }), 404

    return jsonify({
        "advertiser": advertiser.to_dict()
    }), 200


@advertiser_router.route('/', methods=['POST'])
@jwt_required()
@validate_permissions(['advertisers.create'])
def create_advertiser():
    """Create a new advertiser"""
    try:
        # Validate request data
        schema = AdvertiserSchema()
        data = schema.load(request.json)

        # Get current user for audit
        user_id = get_jwt_identity()

        # Create advertiser
        advertiser = Advertiser(
            name=data['name'],
            company_name=data['company_name'],
            credit_code=data.get('credit_code'),
            contact_person=data['contact_person'],
            contact_phone=data['contact_phone'],
            contact_email=data['contact_email'],
            address=data.get('address'),
            industry=data.get('industry'),
            business_type=data.get('business_type'),
            created_by_id=user_id,
            updated_by_id=user_id
        )

        advertiser.save()

        return jsonify({
            "message": "Advertiser created successfully",
            "advertiser": advertiser.to_dict()
        }), 201

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to create advertiser: {str(e)}"
        }), 500


@advertiser_router.route('/<int:advertiser_id>', methods=['PUT'])
@jwt_required()
def update_advertiser(advertiser_id):
    """Update an existing advertiser"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()

        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'advertisers.update' in claims.get('permissions', []) or
                claims.get('advertiser_id') == advertiser_id):
            return jsonify({
                "error": "Not authorized to update this advertiser"
            }), 403

        # Find advertiser
        advertiser = Advertiser.get_by_id(advertiser_id)
        if not advertiser:
            return jsonify({
                "error": "Advertiser not found"
            }), 404

        # Validate request data
        schema = AdvertiserUpdateSchema()
        data = schema.load(request.json)

        # Get current user for audit
        user_id = get_jwt_identity()

        # Update allowed fields
        for field in data:
            setattr(advertiser, field, data[field])

        # Update audit fields
        advertiser.updated_by_id = user_id

        # Log change in audit log
        advertiser.log_change(user_id, "update", data)

        # Save changes
        advertiser.save()

        return jsonify({
            "message": "Advertiser updated successfully",
            "advertiser": advertiser.to_dict()
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update advertiser: {str(e)}"
        }), 500


@advertiser_router.route('/<int:advertiser_id>/status', methods=['PUT'])
@jwt_required()
@validate_permissions(['advertisers.review'])
def update_advertiser_status(advertiser_id):
    """Update advertiser status (approval workflow)"""
    try:
        # Find advertiser
        advertiser = Advertiser.get_by_id(advertiser_id)
        if not advertiser:
            return jsonify({
                "error": "Advertiser not found"
            }), 404

        # Validate request data
        schema = AdvertiserStatusSchema()
        data = schema.load(request.json)

        # Get current user for audit
        user_id = get_jwt_identity()

        # Update status
        advertiser.set_status(data['status'], user_id, data.get('reason'))

        # Save changes
        advertiser.save()

        return jsonify({
            "message": f"Advertiser status updated to {data['status']}",
            "advertiser": advertiser.to_dict()
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to update advertiser status: {str(e)}"
        }), 500


@advertiser_router.route('/<int:advertiser_id>/upload', methods=['POST'])
@jwt_required()
def upload_qualification_file(advertiser_id):
    """Upload qualification documents for advertiser"""
    try:
        # Get JWT claims to check for permissions
        claims = get_jwt()

        # Check permissions or ownership
        if not (claims.get('is_superuser') or 'advertisers.upload' in claims.get('permissions', []) or
                claims.get('advertiser_id') == advertiser_id):
            return jsonify({
                "error": "Not authorized to upload files for this advertiser"
            }), 403

        # Find advertiser
        advertiser = Advertiser.get_by_id(advertiser_id)
        if not advertiser:
            return jsonify({
                "error": "Advertiser not found"
            }), 404

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
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'qualifications', str(advertiser_id))
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # Get file info
        file_size = os.path.getsize(file_path)
        file_type = request.form.get('file_type', 'business_license')

        # Get current user for audit
        user_id = get_jwt_identity()

        # Create qualification file record
        qual_file = QualificationFile(
            advertiser_id=advertiser_id,
            file_path=os.path.join('qualifications', str(advertiser_id), unique_filename),
            file_type=file_type,
            file_size=file_size,
            original_name=filename,
            uploaded_by_id=user_id
        )

        qual_file.save()

        # Add document to advertiser's qualification docs
        document_url = os.path.join('qualifications', str(advertiser_id), unique_filename)
        advertiser.add_document(document_url, file_type, user_id)
        advertiser.save()

        return jsonify({
            "message": "File uploaded successfully",
            "file": qual_file.to_dict()
        }), 201

    except Exception as e:
        return jsonify({
            "error": f"Failed to upload file: {str(e)}"
        }), 500


@advertiser_router.route('/<int:advertiser_id>/deposit', methods=['POST'])
@jwt_required()
@validate_permissions(['advertisers.finance'])
def deposit_funds(advertiser_id):
    """Deposit funds to advertiser account"""
    try:
        # Find advertiser
        advertiser = Advertiser.get_by_id(advertiser_id)
        if not advertiser:
            return jsonify({
                "error": "Advertiser not found"
            }), 404

        # Validate request data
        schema = TransactionSchema()
        data = schema.load(request.json)

        # Get current user for audit
        user_id = get_jwt_identity()

        # Deposit funds
        new_balance = advertiser.deposit(
            data['amount'],
            data['transaction_id'],
            user_id
        )

        return jsonify({
            "message": f"Deposit successful. New balance: {new_balance}",
            "balance": new_balance
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Deposit failed: {str(e)}"
        }), 500


@advertiser_router.route('/<int:advertiser_id>/withdraw', methods=['POST'])
@jwt_required()
@validate_permissions(['advertisers.finance'])
def withdraw_funds(advertiser_id):
    """Withdraw funds from advertiser account"""
    try:
        # Find advertiser
        advertiser = Advertiser.get_by_id(advertiser_id)
        if not advertiser:
            return jsonify({
                "error": "Advertiser not found"
            }), 404

        # Validate request data
        schema = TransactionSchema()
        data = schema.load(request.json)

        # Get current user for audit
        user_id = get_jwt_identity()

        # Withdraw funds
        new_balance = advertiser.withdraw(
            data['amount'],
            data['transaction_id'],
            user_id
        )

        return jsonify({
            "message": f"Withdrawal successful. New balance: {new_balance}",
            "balance": new_balance
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Withdrawal failed: {str(e)}"
        }), 500
