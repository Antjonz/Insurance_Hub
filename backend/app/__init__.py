"""InsuranceHub Backend Application Factory."""
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://insurancehub:insurancehub@localhost:5432/insurancehub'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

    if config:
        app.config.update(config)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.insurers import insurers_bp
    from app.routes.products import products_bp
    from app.routes.policies import policies_bp
    from app.routes.reports import reports_bp
    from app.routes.sync import sync_bp
    from app.routes.mock_apis import mock_bp

    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(insurers_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(policies_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
    app.register_blueprint(sync_bp, url_prefix='/api')
    app.register_blueprint(mock_bp, url_prefix='/mock')

    @app.route('/api/health')
    def health():
        return {'status': 'healthy', 'service': 'InsuranceHub API'}

    return app
