from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# In-memory storage for demo purposes
# In production, use a proper database
bookings_storage = []

# Static bearer token for authentication
BEARER_TOKEN = os.environ.get('CRM_BEARER_TOKEN', 'crm-static-bearer-token-123')

def authenticate_request():
    """Validate Bearer token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return False
    
    try:
        token_type, token = auth_header.split(' ', 1)
        if token_type.lower() != 'bearer':
            return False
        
        return token == BEARER_TOKEN
    except ValueError:
        return False

@app.route('/api/notify', methods=['POST'])
def receive_booking_notification():
    """Endpoint to receive booking notifications from main service"""
    
    # Authenticate request
    if not authenticate_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid Bearer token required'
        }), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['booking_id', 'user', 'event', 'facilitator_id']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Validate user object
        user_required_fields = ['id', 'email', 'name']
        user_missing_fields = [field for field in user_required_fields if field not in data['user']]
        
        if user_missing_fields:
            return jsonify({
                'error': 'Missing required user fields',
                'missing_fields': user_missing_fields
            }), 400
        
        # Validate event object
        event_required_fields = ['id', 'title', 'type']
        event_missing_fields = [field for field in event_required_fields if field not in data['event']]
        
        if event_missing_fields:
            return jsonify({
                'error': 'Missing required event fields',
                'missing_fields': event_missing_fields
            }), 400
        
        # Store booking notification
        notification = {
            'id': len(bookings_storage) + 1,
            'booking_id': data['booking_id'],
            'user': data['user'],
            'event': data['event'],
            'facilitator_id': data['facilitator_id'],
            'booking_date': data.get('booking_date'),
            'notes': data.get('notes', ''),
            'received_at': datetime.utcnow().isoformat(),
            'status': 'received'
        }
        
        bookings_storage.append(notification)
        
        # Log the notification (in production, use proper logging)
        print(f"[CRM] New booking notification received:")
        print(f"  Booking ID: {data['booking_id']}")
        print(f"  User: {data['user']['name']} ({data['user']['email']})")
        print(f"  Event: {data['event']['title']} ({data['event']['type']})")
        print(f"  Facilitator ID: {data['facilitator_id']}")
        
        return jsonify({
            'message': 'Booking notification received successfully',
            'notification_id': notification['id'],
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 400

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all received booking notifications (for facilitator dashboard)"""
    
    # Authenticate request
    if not authenticate_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid Bearer token required'
        }), 401
    
    try:
        # Filter by facilitator_id if provided
        facilitator_id = request.args.get('facilitator_id', type=int)
        
        filtered_bookings = bookings_storage
        if facilitator_id:
            filtered_bookings = [
                booking for booking in bookings_storage 
                if booking['facilitator_id'] == facilitator_id
            ]
        
        return jsonify({
            'bookings': filtered_bookings,
            'total': len(filtered_bookings)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 400

@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get specific booking notification"""
    
    # Authenticate request
    if not authenticate_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid Bearer token required'
        }), 401
    
    try:
        booking = next((b for b in bookings_storage if b['booking_id'] == booking_id), None)
        
        if not booking:
            return jsonify({
                'error': 'Booking not found'
            }), 404
        
        return jsonify({
            'booking': booking
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CRM Notification Service',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    print("Starting CRM Notification Service...")
    print(f"Bearer Token: {BEARER_TOKEN}")
    app.run(debug=True, port=4001)
