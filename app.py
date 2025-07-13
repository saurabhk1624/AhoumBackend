from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Get config name from environment or use default
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.events import events_bp
    from routes.bookings import bookings_bp
    from routes.facilitators import facilitators_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(facilitators_bp, url_prefix='/api/facilitators')
    
    # Import models to ensure they're registered
    from models import user, event, booking, facilitator
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    app.run(debug=True, port=5000)
