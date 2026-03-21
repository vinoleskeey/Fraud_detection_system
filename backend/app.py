from flask import Flask, send_from_directory
from flask_cors import CORS
from utils.config import Config
from utils.extensions import db, cors
from routes.fraud_routes import fraud_bp
import joblib

def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')
    app.config.from_object(Config)
    
    # Initialize extensions
    cors.init_app(app)
    db.init_app(app)
    
# Load models globally (Flask 2.3+ no before_first_request)
try:
    import routes.fraud_routes
    print('Models loaded successfully')
except Exception as e:
    print(f'Model load error: {e}')

# Register blueprints
app.register_blueprint(fraud_bp, url_prefix='/api')

@app.route('/')
    def home():
        return send_from_directory('../templates', 'index.html')
    
    @app.route('/style.css')
    def style_css():
        return send_from_directory('../static', 'style.css')
    
    @app.route('/app.js')
    def app_js():
        return send_from_directory('../static', 'app.js')
    
    @app.route('/<path:path>')
    def send_static(path):
        return send_from_directory('../static', path)
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

