import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create MySQL database and user if they don't exist"""
    
    # MySQL connection parameters
    mysql_host = os.environ.get('MYSQL_HOST', 'ahoum_mysql')
    mysql_port = int(os.environ.get('MYSQL_PORT', '3306'))
    mysql_root_user = os.environ.get('MYSQL_ROOT_USER', 'root')
    mysql_root_password = os.environ.get('MYSQL_ROOT_PASSWORD', 'ahoum123')
    
    # Database and user to create
    database_name = os.environ.get('MYSQL_DATABASE', 'booking_system')
    db_user = os.environ.get('MYSQL_USER', 'booking_user')
    db_password = os.environ.get('MYSQL_PASSWORD', 'booking_password')
    
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_root_user,
            password=mysql_root_password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{database_name}' created successfully!")
            
            # Create user and grant privileges
            cursor.execute(f"CREATE USER IF NOT EXISTS '{db_user}'@'localhost' IDENTIFIED BY '{db_password}'")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{db_user}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print(f"✅ User '{db_user}' created and granted privileges!")
            
            # Test connection with new user
            test_connection = mysql.connector.connect(
                host=mysql_host,
                port=mysql_port,
                user=db_user,
                password=db_password,
                database=database_name
            )
            
            if test_connection.is_connected():
                print(f"✅ Successfully connected to database '{database_name}' with user '{db_user}'")
                test_connection.close()
            
    except Error as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def test_database_connection():
    """Test database connection with application settings"""
    from app import create_app, db
    
    try:
        app = create_app()
        with app.app_context():
            # Test database connection
            db.session.execute('SELECT 1')
            print("✅ Database connection test successful!")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Setting up MySQL database for Booking System...")
    
    if create_database():
        print("\n🔧 Testing database connection...")
        if test_database_connection():
            print("\n🎉 Database setup completed successfully!")
            print("\nNext steps:")
            print("1. Run: python seed_data.py")
            print("2. Run: python app.py")
        else:
            print("\n❌ Database setup failed. Please check your configuration.")
    else:
        print("\n❌ Failed to create database. Please check your MySQL configuration.")
