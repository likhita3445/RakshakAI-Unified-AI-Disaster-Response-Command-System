from flask import Blueprint, request
from services.fix_service import FixService
from utils.helpers import make_response

fix_bp = Blueprint('fix', __name__, url_prefix='/api/fix')

@fix_bp.route('/action-plan', methods=['POST'])
def generate_action_plan():
    data = request.get_json() or {}
    area_name = data.get('area_name', 'Area A — Yamuna Sector 9')

    plan = {
        'target_zone': area_name,
        'priority_score': 96,
        'urgency': 'CRITICAL',
        'location_coords': '28.6139° N, 77.2090° E',
        'affected_summary': '850 Affected (42 Elderly, 17 Children, 8 Critical)',
        'medical_urgency': 'IMMEDIATE',
        'required_resources': {
            'ambulances': 2,
            'ndrf_teams': 1,
            'water_liters': 500,
            'med_kits': 1
        },
        'recommended_route': 'Route B (Highland Bypass)',
        'tactical_steps': [
            'Dispatch 2 Ambulances from Command Base via Route B immediately.',
            'Alert NDRF Team 3 for rubber boat deployment across flooded riverbank.',
            'Air-drop 500L Water & Medical Kits to Sector 9 Community Center roof.',
            'Redirect incoming traffic away from Highway Bridge 4.'
        ]
    }
    return make_response(success=True, data=plan, message="SOS Action Plan generated")

@fix_bp.route('/reroute', methods=['POST'])
def reroute_vehicles():
    data = request.get_json() or {}
    origin = data.get('origin', 'Command Base')
    destination = data.get('destination', 'Area A')

    route_data = FixService.compute_dynamic_safe_route(origin, destination)
    return make_response(success=True, data=route_data, message="Dynamic reroute computed")

@fix_bp.route('/allocate', methods=['POST'])
def allocate_resources():
    data = request.get_json() or {}
    areas = data.get('areas', [])
    inventory = data.get('inventory', {})

    allocations = FixService.optimize_resource_allocation(areas, inventory)
    return make_response(success=True, data=allocations, message="Resources optimized")
