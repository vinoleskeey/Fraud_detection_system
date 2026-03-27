import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory
from flask_cors import CORS
from utils.config import Config
from utils.extensions import db, cors


def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')
    app.config.from_object(Config)

    cors.init_app(app)
    db.init_app(app)

    try:
        from routes.fraud_routes import fraud_bp
        app.register_blueprint(fraud_bp, url_prefix='/api')
        print('Routes loaded successfully')
    except Exception as e:
        print(f'Route load error: {e}')

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
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true',
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
    )
