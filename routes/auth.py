from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as http_requests
from extensions import db
from models.user import User
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Google token is required'}), 400
        
        # Verify Google token
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                Config.GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
        except ValueError as e:
            return jsonify({'error': 'Invalid Google token'}), 401
        
        google_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if email exists with different auth provider
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'Email already registered with different provider'}), 409
            
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                google_id=google_id,
            )
            db.session.add(user)
            db.session.commit()
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Google login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = (int(get_jwt_identity()))
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 400
        
        access_token = create_access_token(identity=str(current_user_id))
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = (int(get_jwt_identity()))
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 400
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
