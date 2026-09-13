"""
RakshakAI - Test Suite for Rescue Action Planning, Reroute Pathfinder & Resource Allocation
"""

import unittest
import sys
import os

# Add project root and backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.services.fix_service import FixService
from ai.local_model import local_model


class TestFixService(unittest.TestCase):
    """Test dynamic routing, resource optimization, and rescue plan generation."""

    def test_dynamic_reroute_recommends_safe_bypass(self):
        """Verify pathfinding picks safe Route B when Route A is submerged."""
        route_data = FixService.compute_dynamic_safe_route('Command Base', 'Area A')
        
        self.assertEqual(route_data['origin'], 'Command Base')
        self.assertEqual(route_data['destination'], 'Area A')
        self.assertIn('recommended_route', route_data)
        
        rec = route_data['recommended_route']
        self.assertEqual(rec['name'], 'Route B (Highland Bypass)')
        self.assertEqual(rec['status'], 'RECOMMENDED')
        self.assertGreaterEqual(rec['safety_score'], 90)

    def test_resource_optimization_fair_allocation(self):
        """Test multi-zone resource distribution prioritizes higher score zones."""
        areas = [
            {'id': 'area-a', 'name': 'Area A', 'severityScore': 94, 'affected': 850},
            {'id': 'area-b', 'name': 'Area B', 'severityScore': 72, 'affected': 420},
            {'id': 'area-c', 'name': 'Area C', 'severityScore': 38, 'affected': 180}
        ]
        inventory = {'ambulances': 5, 'ndrf': 3, 'water': 1200}
        
        allocations = FixService.optimize_resource_allocation(areas, inventory)
        self.assertEqual(len(allocations), 3)

        # Area A (Score 94) should receive 2 ambulances and 1 rescue team
        area_a_alloc = next(a for a in allocations if a['area_id'] == 'area-a')
        self.assertEqual(area_a_alloc['allocated_resources']['ambulances'], 2)
        self.assertEqual(area_a_alloc['allocated_resources']['rescue_teams'], 1)

        # Area C (Score 38) should receive 0 ambulances
        area_c_alloc = next(a for a in allocations if a['area_id'] == 'area-c')
        self.assertEqual(area_c_alloc['allocated_resources']['ambulances'], 0)

    def test_local_ai_action_plan_generator(self):
        """Test SOS Action Plan generation with steps and resources."""
        plan = local_model.generate_action_plan('Area A — Yamuna Sector 9')
        
        self.assertEqual(plan['target_zone'], 'Area A — Yamuna Sector 9')
        self.assertEqual(plan['urgency'], 'CRITICAL')
        self.assertGreaterEqual(plan['priority_score'], 90)
        self.assertIn('tactical_steps', plan)
        self.assertGreaterEqual(len(plan['tactical_steps']), 4)
        self.assertIn('required_resources', plan)
        self.assertGreater(plan['required_resources']['ambulances'], 0)


if __name__ == '__main__':
    unittest.main()
