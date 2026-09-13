"""
RakshakAI - Local Offline AI Decision Engine
Zero-dependency, high-speed local inference engine for disaster response,
NLP emergency extraction, dynamic priority scoring, and action plan generation.
"""

import os
import re
import json

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), 'prompts')


class LocalDisasterModel:
    """
    Offline Rule-based & Heuristic AI Engine for RakshakAI.
    Operates without internet connection or external API keys.
    """

    def __init__(self):
        self._load_prompts()

    def _load_prompts(self):
        self.explain_prompt_template = ""
        self.fix_prompt_template = ""
        
        explain_path = os.path.join(PROMPTS_DIR, 'explain_prompt.txt')
        fix_path = os.path.join(PROMPTS_DIR, 'fix_prompt.txt')

        if os.path.exists(explain_path):
            with open(explain_path, 'r', encoding='utf-8') as f:
                self.explain_prompt_template = f.read()

        if os.path.exists(fix_path):
            with open(fix_path, 'r', encoding='utf-8') as f:
                self.fix_prompt_template = f.read()

    def format_explain_prompt(self, area_data):
        vulnerable = area_data.get('vulnerable', {})
        return self.explain_prompt_template.format(
            area_id=area_data.get('id', 'area-a'),
            area_name=area_data.get('name', 'Area A — Yamuna Riverbank Zone'),
            affected_population=area_data.get('affected', 850),
            elderly_count=vulnerable.get('elderly', 42),
            children_count=vulnerable.get('children', 17),
            critical_count=vulnerable.get('critical', 8),
            disabled_count=vulnerable.get('disabled', 12),
            medical_crisis='YES - URGENT' if area_data.get('medicalNeed', True) else 'NO',
            route_status=area_data.get('routeStatus', 'BLOCKED_PRIMARY'),
            flood_level=area_data.get('floodLevel', 65),
            priority_score=area_data.get('severityScore', 94),
            urgency_level=area_data.get('severity', 'CRITICAL')
        )

    def format_fix_prompt(self, area_data, inventory=None):
        inventory = inventory or {'ambulances': 5, 'ndrf': 3, 'water': 1200, 'medkits': 10}
        vulnerable = area_data.get('vulnerable', {})
        vuln_str = f"{vulnerable.get('critical', 8)} critical, {vulnerable.get('elderly', 42)} elderly, {vulnerable.get('children', 17)} children"
        
        return self.fix_prompt_template.format(
            area_name=area_data.get('name', 'Area A — Yamuna Riverbank Zone'),
            coordinates=area_data.get('coordinates', '28.6139° N, 77.2090° E'),
            affected_count=area_data.get('affected', 850),
            vulnerable_summary=vuln_str,
            medical_urgency='IMMEDIATE EVACUATION' if area_data.get('medicalNeed', True) else 'STABLE',
            blocked_routes=area_data.get('routeStatus', 'Highway Bridge 4 BLOCKED'),
            recommended_route=area_data.get('recommendedRoute', 'Route B (Highland Bypass)'),
            available_ambulances=inventory.get('ambulances', 5),
            available_ndrf=inventory.get('ndrf', 3),
            available_water=inventory.get('water', 1200),
            available_medkits=inventory.get('medkits', 10)
        )

    def explain_decision(self, area_id='area-a'):
        """
        Generate detailed mathematical decision explainability breakdown.
        """
        mock_areas = {
            'area-a': {
                'id': 'area-a',
                'name': 'Area A — Yamuna Riverbank Zone',
                'affected': 850,
                'vulnerable': {'elderly': 42, 'children': 17, 'critical': 8, 'disabled': 12},
                'medicalNeed': True,
                'routeStatus': 'BLOCKED_PRIMARY',
                'floodLevel': 65,
                'severityScore': 94,
                'severity': 'CRITICAL'
            },
            'area-b': {
                'id': 'area-b',
                'name': 'Area B — North District Sector 4',
                'affected': 420,
                'vulnerable': {'elderly': 12, 'children': 5, 'critical': 2, 'disabled': 4},
                'medicalNeed': False,
                'routeStatus': 'CLEAR',
                'floodLevel': 40,
                'severityScore': 72,
                'severity': 'HIGH'
            },
            'area-c': {
                'id': 'area-c',
                'name': 'Area C — East Colony Shelter',
                'affected': 180,
                'vulnerable': {'elderly': 5, 'children': 2, 'critical': 0, 'disabled': 1},
                'medicalNeed': False,
                'routeStatus': 'CLEAR',
                'floodLevel': 25,
                'severityScore': 38,
                'severity': 'MEDIUM'
            }
        }
        area = mock_areas.get(area_id, mock_areas['area-a'])

        pop_pts = min(30, int((area['affected'] / 1000) * 30))
        vuln = area['vulnerable']
        vuln_raw = (vuln['elderly'] * 0.3) + (vuln['children'] * 0.2) + (vuln['critical'] * 1.5) + (vuln['disabled'] * 0.4)
        vuln_pts = min(25, int(vuln_raw * 1.2))
        med_pts = 15 if area['medicalNeed'] else 0
        route_pts = 16 if 'BLOCKED' in area['routeStatus'] else 8
        flood_pts = int((area['floodLevel'] / 100) * 14)

        factors = [
            {'factor': '1. Population Exposure Weight (Max 30 pts)', 'score': pop_pts, 'formula': f'{area["affected"]} / 1000 * 30 pts', 'impact': f'{area["affected"]} residents exposed to direct floodwaters.'},
            {'factor': '2. High-Vulnerability Demographics (Max 25 pts)', 'score': vuln_pts, 'formula': 'Σ(Elderly*0.3 + Child*0.2 + Critical*1.5 + Disabled*0.4)', 'impact': f'{vuln["critical"]} critical patients, {vuln["elderly"]} elderly, {vuln["children"]} children require specialized aid.'},
            {'factor': '3. Acute Medical Emergency Need (15 pts)', 'score': med_pts, 'formula': 'Active hospital/urgent life support flags', 'impact': 'Active oxygen/trauma emergency detected.' if med_pts else 'Standard non-trauma relief.'},
            {'factor': '4. Route Inaccessibility Penalty (Max 16 pts)', 'score': route_pts, 'formula': 'Primary bridge blockage hazard index', 'impact': 'Highway Bridge submerged. Mandatory reroute via Route B.' if route_pts >= 16 else 'Direct highway transit operational.'},
            {'factor': '5. Inundation & Rising Water Factor (Max 14 pts)', 'score': flood_pts, 'formula': f'Inundation depth {area["floodLevel"]}% of critical crest', 'impact': f'Current water level is at {area["floodLevel"]}% crest capacity.'}
        ]

        total = sum(f['score'] for f in factors)

        return {
            'area_id': area['id'],
            'area_name': area['name'],
            'total_score': total,
            'urgency': area['severity'],
            'factors': factors,
            'rationale': f"{area['name']} was classified as {area['severity']} priority (Score: {total}/100) because {vuln['critical']} critical patients and {area['affected']} residents are trapped with primary access bridge blocked.",
            'prompt_used': self.format_explain_prompt(area)
        }

    def generate_action_plan(self, area_name='Area A — Yamuna Sector 9'):
        """
        Generate actionable rescue action plan and resource allocation.
        """
        is_critical = 'Area A' in area_name or 'Yamuna' in area_name
        return {
            'target_zone': area_name,
            'urgency': 'CRITICAL' if is_critical else 'HIGH',
            'priority_score': 96 if is_critical else 74,
            'location_coords': '28.6139° N, 77.2090° E' if is_critical else '28.6640° N, 77.2090° E',
            'affected_summary': '850 Citizens in Flood Sector' if is_critical else '420 Residents',
            'medical_urgency': 'IMMEDIATE — Trauma & Evacuation' if is_critical else 'STANDARD RELIEF',
            'recommended_route': 'Route B (Highland Bypass via Old Cantt Road)' if is_critical else 'Route A (Direct Highway)',
            'required_resources': {
                'ambulances': 2 if is_critical else 1,
                'ndrf_teams': 1 if is_critical else 0,
                'water_liters': 500 if is_critical else 200,
                'food_kits': 300 if is_critical else 150,
                'med_kits': 1 if is_critical else 0
            },
            'tactical_steps': [
                '1. Dispatch 2 Advanced Life Support Ambulances from Command Base via Route B (Highland Bypass) immediately.',
                '2. Deploy NDRF Team 3 with motorized inflatable rubber boats across Yamuna riverbank quadrant.',
                '3. Air-drop 500L drinking water & critical medical triage kits onto Community Center rooftop.',
                '4. Divert all non-emergency traffic away from Highway Bridge 4 due to 1.4m submerged floodwater.'
            ],
            'agency_assignments': {
                'NDRF': 'Deploy 1 rubber boat squad at Sector 9 bank.',
                'Medical_Corps': 'Route 2 ALS ambulances via Route B to Community Center.',
                'Traffic_Police': 'Erect barricades at Highway Bridge 4 and enforce Route B bypass.',
                'SDRF_Logistics': 'Stage 500L drinking water packets at Command Depot.'
            }
        }

    def parse_emergency_nlp(self, text, lang='hi'):
        """
        Extract emergency entities, vulnerable counts, and calculate priority.
        """
        lower = text.lower()
        disaster = 'Flood / Inundation'
        if any(w in lower for w in ['fire', 'aag', 'burn']):
            disaster = 'Fire Outbreak'
        elif any(w in lower for w in ['landslide', 'chatan', 'girna']):
            disaster = 'Landslide'

        numbers = [int(s) for s in re.findall(r'\b\d+\b', text)]
        affected = numbers[0] if numbers else 25

        vulnerable = {'elderly': 0, 'children': 0, 'critical': 0}
        if any(w in lower for w in ['elderly', 'bujurg', 'old']):
            vulnerable['elderly'] += 2
        if any(w in lower for w in ['child', 'bacche', 'school', 'student']):
            vulnerable['children'] += 5
        if any(w in lower for w in ['medicine', 'patient', 'hospital', 'critical', 'ghayal']):
            vulnerable['critical'] += 1

        medical_need = any(w in lower for w in ['medicine', 'dawa', 'doctor', 'patient', 'hospital', 'injured', 'ghayal', 'trauma'])
        is_blocked = any(w in lower for w in ['blocked', 'band', 'submerged', 'doob', 'pani'])

        return {
            'disaster_type': disaster,
            'estimated_affected': affected,
            'vulnerable_breakdown': vulnerable,
            'medical_emergency': medical_need,
            'route_blocked': is_blocked,
            'priority_score': 94 if (medical_need or is_blocked) else 65,
            'urgency': 'CRITICAL' if (medical_need or is_blocked) else 'HIGH',
            'recommended_dispatch': 'NDRF Boat Squad + 2 Ambulances via Route B'
        }


# Global singleton instance
local_model = LocalDisasterModel()
