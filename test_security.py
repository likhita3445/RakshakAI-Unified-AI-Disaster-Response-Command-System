"""
RakshakAI - Test Suite for Multi-Agency Security, RBAC, Secret Detection & Audit Logging
"""

import unittest
import sys
import os

# Add project root and backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from security.security_rules import SecurityRules
from security.secret_detector import SecretDetector
from backend.services.security_service import SecurityService


class TestSecurity(unittest.TestCase):
    """Test RBAC clearance, input sanitization, secret detection, and audit chains."""

    def test_multi_agency_clearance_rbac(self):
        """Test agency authorization permissions."""
        # Commander can perform any action
        self.assertTrue(SecurityRules.validate_agency_clearance('COMMANDER', 'OVERRIDE_AI'))
        self.assertTrue(SecurityRules.validate_agency_clearance('COMMANDER', 'SATELLITE_RECON'))

        # NDRF can perform boat rescue and evacuation, but not traffic lockdown
        self.assertTrue(SecurityRules.validate_agency_clearance('NDRF', 'BOAT_RESCUE'))
        self.assertTrue(SecurityRules.validate_agency_clearance('NDRF', 'EVACUATION'))
        self.assertFalse(SecurityRules.validate_agency_clearance('NDRF', 'TRAFFIC_LOCKDOWN'))

        # Police can do traffic lockdown, but not triage admission
        self.assertTrue(SecurityRules.validate_agency_clearance('POLICE', 'TRAFFIC_LOCKDOWN'))
        self.assertFalse(SecurityRules.validate_agency_clearance('POLICE', 'TRIAGE_ADMISSION'))

        # Invalid agency should be rejected
        self.assertFalse(SecurityRules.validate_agency_clearance('UNKNOWN_AGENCY', 'ANY_ACTION'))

    def test_input_sanitization_xss(self):
        """Test sanitization against malicious script tags in emergency reports."""
        dirty_input = "<script>alert('XSS')</script>Trapped near Sector 9 bridge! Need help."
        clean = SecurityRules.sanitize_input(dirty_input)
        self.assertNotIn('<script>', clean)
        self.assertNotIn('</script>', clean)
        self.assertIn('Trapped near Sector 9 bridge!', clean)

    def test_secret_detection_and_masking(self):
        """Test detection and masking of API keys and private tokens."""
        leaked_payload = "OpenAI key sk-abcdef1234567890abcdef1234567890abcdef and Gemini AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q"
        findings = SecretDetector.scan_text(leaked_payload)
        
        self.assertEqual(len(findings), 2)
        types = [f['type'] for f in findings]
        self.assertIn('OPENAI_API_KEY', types)
        self.assertIn('GOOGLE_GEMINI_KEY', types)

        masked = SecretDetector.mask_secrets(leaked_payload)
        self.assertNotIn('sk-abcdef1234567890abcdef1234567890abcdef', masked)
        self.assertIn('REDACTED', masked)

    def test_cryptographic_audit_log_chain(self):
        """Verify SHA-256 tamper-proof chain of custody for legal and judicial inquiry."""
        chain = []
        entry1 = SecurityRules.create_tamper_proof_audit_entry('NDRF', 'BOAT_DISPATCH', {'area': 'Sector 9'})
        chain.append(entry1)

        entry2 = SecurityRules.create_tamper_proof_audit_entry('POLICE', 'ROUTE_BARRICADE', {'bridge': 'Bridge 4'}, previous_hash=entry1['hash'])
        chain.append(entry2)

        # Valid chain verification
        self.assertTrue(SecurityRules.verify_audit_chain(chain))

        # Tampered entry verification failure
        chain[0]['details']['area'] = 'TAMPERED_AREA'
        self.assertFalse(SecurityRules.verify_audit_chain(chain))

    def test_backend_security_service_offline_sync(self):
        """Test syncing offline reports submitted during cellular network outages."""
        queued_reports = [
            {'id': 'off-1', 'text': 'Offline SOS message 1', 'timestamp': '2026-08-25T01:00:00Z'},
            {'id': 'off-2', 'text': 'Offline SOS message 2', 'timestamp': '2026-08-25T01:05:00Z'}
        ]
        result = SecurityService.sync_offline_reports(queued_reports)
        self.assertEqual(result['synced_count'], 2)
        self.assertEqual(result['status'], 'SYNC_COMPLETE')


if __name__ == '__main__':
    unittest.main()
