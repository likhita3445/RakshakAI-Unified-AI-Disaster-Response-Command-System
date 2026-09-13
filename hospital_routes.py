"""
RakshakAI — Hospital & Emergency Relief Shelter Flask Routes
Blueprint for querying nearby hospitals, checking in families, and SOS dispatch.
"""

from flask import Blueprint, request, jsonify
from services.hospital_service import (
    get_nearest_facilities,
    register_family_checkin,
    broadcast_sos_emergency,
    SHELTERS_DATA,
    FAMILY_CHECKINS
)

hospital_bp = Blueprint('hospital', __name__, url_prefix='/api/shelters')


@hospital_bp.route('/nearest', methods=['GET'])
def nearest_shelters():
    """
    GET /api/shelters/nearest?lat=28.6139&lng=77.2090&type=ALL&radius=30
    Returns list of hospitals and relief shelters sorted by proximity.
    """
    try:
        lat = float(request.args.get('lat', 28.6139))
        lng = float(request.args.get('lng', 77.2090))
        facility_type = request.args.get('type', 'ALL').upper()
        radius = float(request.args.get('radius', 30.0))

        facilities = get_nearest_facilities(user_lat=lat, user_lng=lng, facility_type=facility_type, max_radius_km=radius)

        return jsonify({
            'success': True,
            'data': facilities,
            'count': len(facilities),
            'query': {
                'lat': lat,
                'lng': lng,
                'type': facility_type,
                'radius_km': radius
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@hospital_bp.route('/check-in', methods=['POST'])
def family_checkin():
    """
    POST /api/shelters/check-in
    Registers family members safe at a specific relief shelter or hospital.
    """
    try:
        data = request.get_json() or {}
        res = register_family_checkin(data)
        status_code = 201 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@hospital_bp.route('/check-ins', methods=['GET'])
def list_checkins():
    """
    GET /api/shelters/check-ins
    List recent family check-ins for reunification lookup.
    """
    return jsonify({
        'success': True,
        'data': FAMILY_CHECKINS,
        'count': len(FAMILY_CHECKINS)
    }), 200


@hospital_bp.route('/sos/broadcast', methods=['POST'])
def sos_broadcast():
    """
    POST /api/shelters/sos/broadcast
    Citizens trigger high-priority SOS, notifying family and deploying nearest medical response.
    """
    try:
        payload = request.get_json() or {}
        res = broadcast_sos_emergency(payload)
        return jsonify(res), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
