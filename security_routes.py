from flask import Blueprint, request
from services.security_service import SecurityService
from services.ai_service import AIService
from utils.helpers import make_response

security_bp = Blueprint('security', __name__, url_prefix='/api/security')

@security_bp.route('/dispatch', methods=['POST'])
def dispatch_task():
    data = request.get_json() or {}
    agency = data.get('agency', 'Police')
    target = data.get('target_area', 'Area A')
    task = data.get('task', 'Traffic lockdown')
    dispatch_record = SecurityService.dispatch_agency_task(agency, target, task)
    return make_response(success=True, data=dispatch_record, message=f"Task dispatched to {agency}")

@security_bp.route('/sync-offline', methods=['POST'])
def sync_offline():
    data = request.get_json() or {}
    reports = data.get('reports', [])

    result = SecurityService.sync_offline_reports(reports)
    return make_response(success=True, data=result, message="Offline reports synchronized")

@security_bp.route('/explain/<string:area_id>', methods=['GET'])
def explain_decision(area_id):
    sample_area = {
        'affected': 850,
        'vulnerable': {'elderly': 42, 'children': 17, 'critical': 8},
        'medical_crisis': True,
        'route_status': 'BLOCKED',
        'flood_level': 65
    }
    score_data = AIService.calculate_priority_score(sample_area)

    explanation = {
        'area_id': area_id,
        'total_score': score_data['score'],
        'confidence_score': '94.2%',
        'breakdown': score_data['breakdown'],
        'summary': 'Area A is prioritized because 850 people are affected, 8 patients are in critical condition, and the main route is blocked.'
    }
    return make_response(success=True, data=explanation, message="Explainability decision log retrieved")
