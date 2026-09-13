from flask import Flask, jsonify
from config import Config
from routes.analysis_routes import analysis_bp
from routes.fix_routes import fix_bp
from routes.test_routes import test_bp
from routes.security_routes import security_bp
from routes.hospital_routes import hospital_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS Headers - Allow all origins for frontend access
    @app.after_request
    def apply_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    # Handle OPTIONS preflight requests
    @app.before_request
    def handle_options():
        from flask import request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            return response, 200

    # Register Blueprints
    app.register_blueprint(analysis_bp)
    app.register_blueprint(fix_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(hospital_bp)

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'system': 'RakshakAI Backend REST Engine',
            'version': '2.0.0',
            'status': 'OPERATIONAL',
            'blueprints': ['/api/analysis', '/api/fix', '/api/test', '/api/security', '/api/shelters']
        })

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'HEALTHY',
            'ai_engine': 'ONLINE',
            'pathfinding_router': 'ACTIVE',
            'nlp_parser': 'ACTIVE'
        })

    return app


app = create_app()

if __name__ == '__main__':
    print("[RAKSHAKAI] Starting Flask Backend Server on http://127.0.0.1:5000")
    print("[RAKSHAKAI] CORS enabled — frontend can connect from any origin")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
