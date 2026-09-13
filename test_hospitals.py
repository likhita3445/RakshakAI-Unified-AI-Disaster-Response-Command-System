"""
RakshakAI - Test Suite for Hospital & Emergency Relief Shelter Services & Routes
"""

import unittest
import json
import sys
import os

# Add project root and backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.app import app
from backend.services.hospital_service import haversine_distance_km, get_nearest_facilities


class TestHospitalService(unittest.TestCase):
    """Test geospatial calculation and hospital/shelter retrieval logic."""

    def test_haversine_distance(self):
        """Haversine distance calculation is accurate."""
        # Distance between Connaught Place (28.6315, 77.2167) and India Gate (28.6129, 77.2295) is ~2.3 km
        dist = haversine_distance_km(28.6315, 77.2167, 28.6129, 77.2295)
        self.assertAlmostEqual(dist, 2.4, delta=0.5)

    def test_get_nearest_facilities_sorted(self):
        """Nearest facilities are returned sorted by ascending distance."""
        facilities = get_nearest_facilities(user_lat=28.6139, user_lng=77.2090, facility_type="ALL")
        self.assertGreater(len(facilities), 0)
        # Check ascending order
        for i in range(len(facilities) - 1):
            self.assertLessEqual(facilities[i]["distance_km"], facilities[i + 1]["distance_km"])

    def test_filter_by_facility_type(self):
        """Filtering by HOSPITAL returns only hospitals."""
        hospitals = get_nearest_facilities(user_lat=28.6139, user_lng=77.2090, facility_type="HOSPITAL")
        for h in hospitals:
            self.assertEqual(h["type"], "HOSPITAL")


class TestHospitalRoutes(unittest.TestCase):
    """Test Flask endpoints for hospitals, shelters, family check-in, and SOS broadcast."""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_nearest_shelters_endpoint(self):
        """GET /api/shelters/nearest returns nearby shelters and hospitals."""
        res = self.client.get('/api/shelters/nearest?lat=28.6139&lng=77.2090&type=ALL&radius=25')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 1)
        first = data['data'][0]
        self.assertIn('name', first)
        self.assertIn('distance_km', first)
        self.assertIn('available_beds', first)

    def test_family_checkin_endpoint(self):
        """POST /api/shelters/check-in registers family members safely."""
        payload = {
            'shelter_id': 'shelter-north-01',
            'primary_contact_name': 'Ramesh Kumar',
            'phone': '+91-98765-43210',
            'members_count': 4,
            'names': ['Ramesh', 'Sunita', 'Aarav', 'Ananya'],
            'medical_needs': 'Insulin for elderly'
        }
        res = self.client.post('/api/shelters/check-in', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['members_count'], 4)
        self.assertEqual(data['data']['status'], 'SAFELY_SHELTERED')

    def test_sos_broadcast_endpoint(self):
        """POST /api/shelters/sos/broadcast triggers multi-agency emergency response."""
        payload = {
            'caller_name': 'Vikram Mehra',
            'phone': '+91-99887-76655',
            'emergency_type': 'FLOOD_INUNDATION',
            'lat': 28.6139,
            'lng': 77.2090
        }
        res = self.client.post('/api/shelters/sos/broadcast', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('closest_hospital', data['data'])
        self.assertIn('dispatched_agencies', data['data'])
        self.assertIn('family_contacts_alerted', data['data'])


if __name__ == '__main__':
    unittest.main()
