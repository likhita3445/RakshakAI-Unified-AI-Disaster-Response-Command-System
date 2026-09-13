"""
RakshakAI - Test Suite for AI Analysis, NLP & Priority Scoring Engine
"""

import unittest
import sys
import os

# Add project root and backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.services.ai_service import AIService
from ai.local_model import LocalDisasterModel, local_model


class TestAIAnalysis(unittest.TestCase):
    """Test AI priority calculation, NLP extraction, and simulation logic."""

    def setUp(self):
        self.ai = AIService()
        self.local_ai = local_model

    def test_priority_score_calculation_critical(self):
        """Test calculation of high-severity disaster area."""
        area_data = {
            'affected': 1200,
            'vulnerable': {'elderly': 50, 'children': 30, 'critical': 10, 'disabled': 15},
            'medical_crisis': True,
            'route_status': 'BLOCKED_PRIMARY',
            'flood_level': 85
        }
        result = AIService.calculate_priority_score(area_data)
        self.assertGreaterEqual(result['score'], 85)
        self.assertEqual(result['urgency_level'], 'CRITICAL')
        self.assertEqual(len(result['breakdown']), 5)

    def test_priority_score_calculation_low_severity(self):
        """Test calculation for low-risk zone."""
        area_data = {
            'affected': 50,
            'vulnerable': {'elderly': 1, 'children': 0, 'critical': 0, 'disabled': 0},
            'medical_crisis': False,
            'route_status': 'CLEAR',
            'flood_level': 10
        }
        result = AIService.calculate_priority_score(area_data)
        self.assertLessEqual(result['score'], 50)
        self.assertIn(result['urgency_level'], ['MEDIUM', 'LOW', 'HIGH'])

    def test_nlp_parsing_hindi_flood_report(self):
        """Test Hindi voice report containing flood, children count, and medicine."""
        report_text = "Yamuna ke paas paani bahut badh gaya hai, 30 log fase hain aur elderly ko medicine chahiye!"
        parsed = AIService.parse_multilingual_report(report_text, lang='hi')
        
        self.assertEqual(parsed['disaster_type'], 'Flood / Inundation')
        self.assertTrue(parsed['medical_emergency'])
        self.assertGreaterEqual(parsed['estimated_affected'], 15)
        self.assertGreater(parsed['priority_score'], 70)

    def test_nlp_parsing_english_fire_report(self):
        """Test English report with fire outbreak and injuries."""
        report_text = "Massive fire outbreak near warehouse! 12 people injured and hospital ambulance needed immediately."
        parsed = AIService.parse_multilingual_report(report_text, lang='en')
        
        self.assertEqual(parsed['disaster_type'], 'Fire Outbreak')
        self.assertTrue(parsed['medical_emergency'])

    def test_nlp_parsing_landslide(self):
        """Test landslide keyword detection in regional Hinglish."""
        report_text = "Pahad se chatan girna shuru ho gaya hai, road band hai."
        parsed = AIService.parse_multilingual_report(report_text, lang='hi')
        
        self.assertEqual(parsed['disaster_type'], 'Landslide')

    def test_explainability_decision_factors(self):
        """Verify mathematical explainability output structure."""
        explanation = self.local_ai.explain_decision('area-a')
        self.assertEqual(explanation['area_id'], 'area-a')
        self.assertIn('total_score', explanation)
        self.assertIn('factors', explanation)
        self.assertEqual(len(explanation['factors']), 5)
        self.assertTrue(any('Population' in f['factor'] for f in explanation['factors']))


if __name__ == '__main__':
    unittest.main()
