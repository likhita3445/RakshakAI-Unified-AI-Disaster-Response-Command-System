import os

class Config:
    """
    RakshakAI Master Configuration & AI Decision System Parameters
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'rakshakai_secret_key_2026_hackathon_win')
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'

    # Priority Scoring Weights
    WEIGHT_POPULATION = 0.30
    WEIGHT_VULNERABLE = 0.25
    WEIGHT_MEDICAL_CRISIS = 0.15
    WEIGHT_ROUTE_ACCESSIBILITY = 0.16
    WEIGHT_DISASTER_SEVERITY = 0.14

    # Default Base Resources Inventory
    INITIAL_INVENTORY = {
        'ambulances': 8,
        'rescue_teams': 4,
        'water_liters': 2000,
        'food_kits': 1000,
        'medicine_kits': 300
    }

    # NLP Confidence Thresholds
    NLP_CONFIDENCE_THRESHOLD = 0.85
