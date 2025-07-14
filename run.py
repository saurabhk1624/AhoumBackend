#!/usr/bin/env python3
"""
Application runner for the booking system
"""
import os
from app import create_app
from extensions import db

def main():
    """Main application runner"""
    # Set environment if not already set
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Create the Flask application
    app = create_app()
    
    # Ensure all tables are created within app context
    with app.app_context():
        try:
            print("Initializing database...")
            db.create_all()
            print("Database tables created successfully!")
            print(f"Available tables: {list(db.metadata.tables.keys())}")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            print("Application will continue, but database operations may fail")
    
    # Start the application
    print("Starting Flask application...")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print("Access the application at: http://localhost:8000")
    print("Health check at: http://localhost:8000/health")
    print("API documentation at: http://localhost:8000/apidocs")
    
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
        use_reloader=True
    )

if __name__ == '__main__':
    main()