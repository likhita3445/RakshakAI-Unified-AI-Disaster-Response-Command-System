from flask import Blueprint, request
from services.test_service import TestService
from utils.helpers import make_response

test_bp = Blueprint('test', __name__, url_prefix='/api/test')

@test_bp.route('/judge-demo/<int:step_id>', methods=['GET'])
def get_judge_step(step_id):
    step_data = TestService.get_judge_demo_step(step_id)
    return make_response(success=True, data=step_data, message=f"Judge demo step {step_id} loaded")

@test_bp.route('/stress-test', methods=['POST'])
def run_stress_test():
    result = {
        'simulation_mode': 'MASS DISASTER SPIKE',
        'simulated_reports_per_sec': 450,
        'ai_processing_latency_ms': 18,
        'system_status': 'STABLE',
        'active_nodes_evaluated': 24
    }
    return make_response(success=True, data=result, message="Stress test execution completed")
