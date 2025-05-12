from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime, timedelta
import pandas as pd
import json

from app.models.base import db
from app.models.campaign.campaign import Campaign, Creative
from app.models.report.report import Report
from app.utils.validators import validate_permissions
from app.utils.report_generators import (
    generate_campaign_report,
    generate_creative_report,
    generate_advertiser_report,
    generate_platform_report
)

# Create report blueprint
report_router = Blueprint('report', __name__)


class ReportRequestSchema(Schema):
    """Schema for report request validation"""
    report_type = fields.String(required=True, validate=validate.OneOf([
        'campaign', 'creative', 'advertiser', 'platform'
    ]))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    metrics = fields.List(fields.String(), required=True)
    dimensions = fields.List(fields.String(), required=True)
    filters = fields.Dict(allow_none=True)
    group_by = fields.List(fields.String(), allow_none=True)
    sort_by = fields.List(fields.String(), allow_none=True)
    limit = fields.Integer(allow_none=True)


@report_router.route('/generate', methods=['POST'])
@jwt_required()
@validate_permissions(['reports.generate'])
def generate_report():
    """Generate a new report"""
    try:
        # Validate request data
        schema = ReportRequestSchema()
        data = schema.load(request.json)

        # Get current user for audit
        user_id = get_jwt_identity()
        claims = get_jwt()

        # Check date range
        if data['end_date'] - data['start_date'] > timedelta(days=90):
            return jsonify({
                "error": "Date range cannot exceed 90 days"
            }), 400

        # Create report record
        report = Report(
            report_type=data['report_type'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            metrics=json.dumps(data['metrics']),
            dimensions=json.dumps(data['dimensions']),
            filters=json.dumps(data.get('filters', {})),
            group_by=json.dumps(data.get('group_by', [])),
            sort_by=json.dumps(data.get('sort_by', [])),
            limit=data.get('limit'),
            status='pending',
            created_by_id=user_id,
            updated_by_id=user_id
        )

        # Save report
        report.save()

        # Generate report asynchronously
        current_app.task_queue.enqueue(
            'generate_report_task',
            report_id=report.id,
            report_type=data['report_type'],
            start_date=data['start_date'].isoformat(),
            end_date=data['end_date'].isoformat(),
            metrics=data['metrics'],
            dimensions=data['dimensions'],
            filters=data.get('filters', {}),
            group_by=data.get('group_by', []),
            sort_by=data.get('sort_by', []),
            limit=data.get('limit')
        )

        return jsonify({
            "message": "Report generation started",
            "report": report.to_dict()
        }), 202

    except ValidationError as e:
        return jsonify({
            "error": "Validation error",
            "details": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate report: {str(e)}"
        }), 500


@report_router.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    """Get list of reports with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # Get JWT claims to check for advertiser_id
    claims = get_jwt()
    advertiser_id = claims.get('advertiser_id')

    # Filters
    filters = {}
    if advertiser_id and not claims.get('is_superuser'):
        # Regular users can only view their own reports
        filters['advertiser_id'] = advertiser_id

    # Query based on filters
    result = Report.paginate(page=page, per_page=per_page, **filters)

    return jsonify(result), 200


@report_router.route('/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get report details and data"""
    # Get JWT claims to check for permissions
    claims = get_jwt()

    # Find report
    report = Report.get_by_id(report_id)
    if not report:
        return jsonify({
            "error": "Report not found"
        }), 404

    # Check permissions or ownership
    if not (claims.get('is_superuser') or 'reports.view' in claims.get('permissions', []) or
            claims.get('advertiser_id') == report.advertiser_id):
        return jsonify({
            "error": "Not authorized to view this report"
        }), 403

    # If report is still pending, return status
    if report.status == 'pending':
        return jsonify({
            "report": report.to_dict(),
            "status": "pending"
        }), 200

    # If report failed, return error
    if report.status == 'failed':
        return jsonify({
            "report": report.to_dict(),
            "error": report.error_message
        }), 200

    # Return report data
    return jsonify({
        "report": report.to_dict(),
        "data": report.get_data()
    }), 200


@report_router.route('/<int:report_id>/download', methods=['GET'])
@jwt_required()
def download_report(report_id):
    """Download report in specified format"""
    # Get JWT claims to check for permissions
    claims = get_jwt()

    # Find report
    report = Report.get_by_id(report_id)
    if not report:
        return jsonify({
            "error": "Report not found"
        }), 404

    # Check permissions or ownership
    if not (claims.get('is_superuser') or 'reports.download' in claims.get('permissions', []) or
            claims.get('advertiser_id') == report.advertiser_id):
        return jsonify({
            "error": "Not authorized to download this report"
        }), 403

    # Check if report is ready
    if report.status != 'completed':
        return jsonify({
            "error": "Report is not ready for download"
        }), 400

    # Get format from query params
    format = request.args.get('format', 'csv')
    if format not in ['csv', 'excel', 'json']:
        return jsonify({
            "error": "Invalid format. Supported formats: csv, excel, json"
        }), 400

    # Get report data
    data = report.get_data()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Generate file based on format
    if format == 'csv':
        return df.to_csv(index=False), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=report_{report_id}.csv'
        }
    elif format == 'excel':
        return df.to_excel(index=False), 200, {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': f'attachment; filename=report_{report_id}.xlsx'
        }
    else:  # json
        return jsonify(data), 200, {
            'Content-Disposition': f'attachment; filename=report_{report_id}.json'
        }


@report_router.route('/templates', methods=['GET'])
@jwt_required()
def get_report_templates():
    """Get available report templates"""
    templates = {
        'campaign': {
            'name': 'Campaign Performance Report',
            'description': 'Detailed campaign performance metrics',
            'default_metrics': ['impressions', 'clicks', 'ctr', 'spend', 'conversions'],
            'default_dimensions': ['campaign_id', 'campaign_name', 'date'],
            'available_metrics': [
                'impressions', 'clicks', 'ctr', 'spend', 'conversions',
                'conversion_rate', 'cpa', 'cpc', 'cpm', 'roi'
            ],
            'available_dimensions': [
                'campaign_id', 'campaign_name', 'date', 'advertiser_id',
                'advertiser_name', 'status', 'bid_strategy'
            ]
        },
        'creative': {
            'name': 'Creative Performance Report',
            'description': 'Creative-level performance metrics',
            'default_metrics': ['impressions', 'clicks', 'ctr', 'spend'],
            'default_dimensions': ['creative_id', 'creative_name', 'date'],
            'available_metrics': [
                'impressions', 'clicks', 'ctr', 'spend', 'conversions',
                'conversion_rate', 'cpa', 'cpc', 'cpm'
            ],
            'available_dimensions': [
                'creative_id', 'creative_name', 'date', 'campaign_id',
                'campaign_name', 'creative_type', 'status'
            ]
        },
        'advertiser': {
            'name': 'Advertiser Performance Report',
            'description': 'Advertiser-level performance summary',
            'default_metrics': ['impressions', 'clicks', 'spend', 'conversions'],
            'default_dimensions': ['advertiser_id', 'advertiser_name', 'date'],
            'available_metrics': [
                'impressions', 'clicks', 'ctr', 'spend', 'conversions',
                'conversion_rate', 'cpa', 'cpc', 'cpm', 'roi'
            ],
            'available_dimensions': [
                'advertiser_id', 'advertiser_name', 'date', 'status'
            ]
        },
        'platform': {
            'name': 'Platform Performance Report',
            'description': 'Platform-wide performance metrics',
            'default_metrics': ['impressions', 'clicks', 'spend', 'revenue'],
            'default_dimensions': ['date', 'platform'],
            'available_metrics': [
                'impressions', 'clicks', 'ctr', 'spend', 'revenue',
                'profit', 'margin', 'roi'
            ],
            'available_dimensions': [
                'date', 'platform', 'advertiser_id', 'advertiser_name',
                'campaign_id', 'campaign_name'
            ]
        }
    }

    return jsonify(templates), 200
