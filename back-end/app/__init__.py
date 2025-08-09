from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern for Flask app"""
    app = Flask(__name__)
    
    # Import and use your config classes
    from app.config import config
    
    # Determine which config to use
    config_name = config_name or os.environ.get('FLASK_ENV') or 'default'
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    try:
        from app.routes.api import api
        app.register_blueprint(api)
        print("✓ API blueprint registered successfully")
    except ImportError as e:
        print(f"✗ Could not import API blueprint: {e}")
    
    # Test routes
    @app.route('/')
    def hello():
        return {'message': 'Finance KPI API is running!', 'status': 'success'}
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'database': 'connected'}
    
    return app