"""
RakshakAI - Multi-Agency Security & Access Control Rules
Implements Role-Based Access Control (RBAC), multi-agency clearance,
dispatch verification, and cryptographic audit log integrity.
"""

import hashlib
import time
import re
from typing import Dict, List, Optional, Any


class SecurityRules:
    """
    Security validation and clearance rules for multi-agency command.
    """

    # Multi-Agency Role Definitions & Allowed Operations
    AGENCY_ROLES = {
        'COMMANDER': {
            'clearance_level': 5,
            'allowed_actions': ['ALL', 'DISPATCH_ALL', 'OVERRIDE_AI', 'SYSTEM_CONFIG', 'SATELLITE_RECON', 'VIEW_AUDIT']
        },
        'NDRF': {
            'clearance_level': 4,
            'allowed_actions': ['BOAT_RESCUE', 'WATER_AIRDROP', 'EVACUATION', 'VIEW_MAP', 'REPORT_STATUS']
        },
        'POLICE': {
            'clearance_level': 3,
            'allowed_actions': ['TRAFFIC_LOCKDOWN', 'ROUTE_BARRICADE', 'PERIMETER_SECURITY', 'VIEW_MAP']
        },
        'MEDICAL': {
            'clearance_level': 4,
            'allowed_actions': ['AMBULANCE_DISPATCH', 'TRIAGE_ADMISSION', 'MEDKIT_AIRDROP', 'PATIENT_TRANSFER']
        },
        'FIRE': {
            'clearance_level': 3,
            'allowed_actions': ['FIRE_SUPPRESSION', 'STRUCTURAL_COLLAPSE_RESCUE', 'VIEW_MAP']
        },
        'PUBLIC_USER': {
            'clearance_level': 1,
            'allowed_actions': ['SUBMIT_EMERGENCY_REPORT', 'VIEW_PUBLIC_ALERTS', 'VIEW_SHELTERS']
        }
    }

    @staticmethod
    def validate_agency_clearance(agency_name: str, action: str) -> bool:
        """
        Verify whether an agency or user role is authorized to perform a command action.
        """
        agency_upper = agency_name.upper()
        if agency_upper not in SecurityRules.AGENCY_ROLES:
            return False

        role_permissions = SecurityRules.AGENCY_ROLES[agency_upper]['allowed_actions']
        if 'ALL' in role_permissions:
            return True

        return action.upper() in role_permissions or 'DISPATCH_ALL' in role_permissions

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize incoming emergency report text against injection attacks.
        """
        if not text:
            return ""
        # Strip dangerous HTML/Script tags while preserving regional Unicode characters
        clean = re.sub(r'<[^>]*?>', '', text)
        clean = re.sub(r'javascript:', '', clean, flags=re.IGNORECASE)
        return clean.strip()

    @staticmethod
    def create_tamper_proof_audit_entry(agency: str, action: str, details: Dict[str, Any], previous_hash: str = "") -> Dict[str, Any]:
        """
        Create a cryptographically hashed (SHA-256) audit log entry to ensure
        chain-of-custody compliance during post-disaster judicial and government inquiries.
        """
        timestamp = time.time()
        payload = f"{agency}:{action}:{str(details)}:{timestamp}:{previous_hash}"
        entry_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

        return {
            'timestamp': timestamp,
            'agency': agency,
            'action': action,
            'details': details,
            'previous_hash': previous_hash,
            'hash': entry_hash,
            'verified': True
        }

    @staticmethod
    def verify_audit_chain(audit_entries: List[Dict[str, Any]]) -> bool:
        """
        Verify the mathematical integrity of the immutable audit log chain.
        """
        for i, entry in enumerate(audit_entries):
            prev_hash = audit_entries[i - 1]['hash'] if i > 0 else ""
            payload = f"{entry['agency']}:{entry['action']}:{str(entry['details'])}:{entry['timestamp']}:{prev_hash}"
            expected_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
            if entry['hash'] != expected_hash:
                return False
        return True


# Global rules instance
security_rules = SecurityRules()
