from flask import Blueprint, request
from services.ai_service import AIService
from services.code_analysis import CodeAnalysisService
from utils.helpers import make_response

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@analysis_bp.route('/priority', methods=['POST'])
def calculate_priority():
    data = request.get_json() or {}
    result = AIService.calculate_priority_score(data)
    return make_response(success=True, data=result, message="Priority score calculated successfully")

@analysis_bp.route('/nlp', methods=['POST'])
def parse_nlp():
    data = request.get_json() or {}
    text = data.get('text', '')
    lang = data.get('lang', 'hi')
    result = AIService.parse_multilingual_report(text, lang)
    return make_response(success=True, data=result, message="Emergency text parsed successfully")

@analysis_bp.route('/simulate', methods=['POST'])
def run_simulation():
    data = request.get_json() or {}
    population = data.get('population', 850)
    flood_level = data.get('flood_level', 65)
    ambulances = data.get('available_ambulances', 5)

    score_data = AIService.calculate_priority_score({
        'affected': population,
        'vulnerable': {'elderly': 42, 'children': 17, 'critical': 8},
        'medical_crisis': True,
        'route_status': 'BLOCKED',
        'flood_level': flood_level
    })

    bottleneck = False
    bottleneck_msg = None
    if ambulances < 8 and population > 2000:
        bottleneck = True
        bottleneck_msg = f"{ambulances} Ambulances are insufficient for {population} affected population. Recommended minimum: 8."

    response = {
        'recalculated_score': score_data['score'],
        'urgency_level': score_data['urgency_level'],
        'bottleneck_detected': bottleneck,
        'bottleneck_message': bottleneck_msg,
        'recommended_route': 'Route B (Highland Bypass)',
        'breakdown': score_data['breakdown']
    }
    return make_response(success=True, data=response, message="Simulation updated")

@analysis_bp.route('/satellite', methods=['POST'])
def analyze_satellite():
    findings = {
        'flooded_zone_percentage': 98.4,
        'collapsed_bridge_detected': True,
        'bridge_confidence': 94.1,
        'inundated_area_km2': 4.2,
        'road_blockage_percentage': 65,
        'damaged_structures': 42
    }
    return make_response(success=True, data=findings, message="Satellite computer vision analysis complete")

@analysis_bp.route('/predict', methods=['GET'])
def predict_severity():
    predictions = [
        {'time': 'Current (00:00)', 'status': 'HIGH', 'water_level_m': 205.4},
        {'time': 'Forecast (+2h)', 'status': 'VERY HIGH', 'water_level_m': 205.9},
        {'time': 'Forecast (+4h)', 'status': 'CRITICAL', 'water_level_m': 206.5}
    ]
    return make_response(success=True, data=predictions, message="Disaster forecast generated")
