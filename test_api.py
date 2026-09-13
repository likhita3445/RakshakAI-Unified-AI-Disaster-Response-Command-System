"""
RakshakAI - Test Suite for Flask REST API Endpoints & Multi-Route Integration
"""

import unittest
import json
import sys
import os

# Add project root and backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.app import app


class TestRestAPI(unittest.TestCase):
    """Test all Flask REST API routes and JSON contracts."""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_health_check_endpoint(self):
        """GET /api/health returns 200 and HEALTHY status."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'HEALTHY')
        self.assertEqual(data['ai_engine'], 'ONLINE')

    def test_priority_score_endpoint(self):
        """POST /api/analysis/priority returns priority score and breakdown."""
        payload = {
            'affected': 850,
            'vulnerable': {'elderly': 42, 'children': 17, 'critical': 8},
            'medical_crisis': True,
            'route_status': 'BLOCKED',
            'flood_level': 65
        }
        res = self.client.post('/api/analysis/priority', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['data']['score'], 80)
        self.assertEqual(data['data']['urgency_level'], 'CRITICAL')

    def test_nlp_parser_endpoint(self):
        """POST /api/analysis/nlp parses emergency text into structured entities."""
        payload = {
            'text': 'Flood water rising rapidly near Central School! 45 children trapped on 2nd floor.',
            'lang': 'en'
        }
        res = self.client.post('/api/analysis/nlp', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['disaster_type'], 'Flood / Inundation')
        self.assertIn('VulnerableGroups', data['data']['extracted_json'])

    def test_digital_twin_simulation_endpoint(self):
        """POST /api/analysis/simulate returns recalculated metrics and bottleneck alerts."""
        payload = {
            'population': 2500,
            'flood_level': 85,
            'available_ambulances': 3
        }
        res = self.client.post('/api/analysis/simulate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['bottleneck_detected'])
        self.assertIn('Route B', data['data']['recommended_route'])

    def test_satellite_analysis_endpoint(self):
        """POST /api/analysis/satellite returns computer vision flood telemetry."""
        res = self.client.post('/api/analysis/satellite', json={})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['collapsed_bridge_detected'])
        self.assertGreater(data['data']['flooded_zone_percentage'], 90)

    def test_action_plan_generator_endpoint(self):
        """POST /api/fix/action-plan returns immediate tactical step plan."""
        payload = {'area_name': 'Area A — Yamuna Sector 9'}
        res = self.client.post('/api/fix/action-plan', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['urgency'], 'CRITICAL')
        self.assertEqual(len(data['data']['tactical_steps']), 4)

    def test_reroute_endpoint(self):
        """POST /api/fix/reroute returns dynamic safe route alternatives."""
        payload = {'origin': 'Command Base', 'destination': 'Area A'}
        res = self.client.post('/api/fix/reroute', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['recommended_route']['name'], 'Route B (Highland Bypass)')

    def test_security_dispatch_endpoint(self):
        """POST /api/security/dispatch logs and dispatches agency task."""
        payload = {
            'agency': 'NDRF',
            'target_area': 'Yamuna Sector 9',
            'task': 'Rubber boat flood rescue'
        }
        res = self.client.post('/api/security/dispatch', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['agency'], 'NDRF')
        self.assertEqual(data['data']['status'], 'DISPATCHED')

    def test_explainability_endpoint(self):
        """GET /api/security/explain/<area_id> returns decision explainability."""
        res = self.client.get('/api/security/explain/area-a')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['area_id'], 'area-a')
        self.assertIn('breakdown', data['data'])


if __name__ == '__main__':
    unittest.main()
