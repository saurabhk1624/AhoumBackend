from flask import Flask, request, jsonify
from datetime import datetime
import os
import sys
import json

app = Flask(__name__)

# In-memory storage for demo purposes
# In production, you'd use a proper database or Redis
bookings_storage = []
facilitators_cache = {}
events_cache = {}

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

def save_data_to_file():
    """Save data to file for persistence (optional)"""
    try:
        data = {
            'bookings': bookings_storage,
            'facilitators': facilitators_cache,
            'events': events_cache,
            'last_updated': datetime.utcnow().isoformat()
        }
        with open('/tmp/crm_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save data to file: {e}")

def load_data_from_file():
    """Load data from file if exists"""
    try:
        with open('/tmp/crm_data.json', 'r') as f:
            data = json.load(f)
            global bookings_storage, facilitators_cache, events_cache
            bookings_storage = data.get('bookings', [])
            facilitators_cache = data.get('facilitators', {})
            events_cache = data.get('events', {})
            print(f"✅ Loaded {len(bookings_storage)} bookings from file")
    except FileNotFoundError:
        print("ℹ️ No existing data file found, starting fresh")
    except Exception as e:
        print(f"Warning: Could not load data from file: {e}")

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
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Request body must contain JSON data'
            }), 400
        
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
        
        # Check if booking already exists
        existing_booking = next((b for b in bookings_storage if b['booking_id'] == data['booking_id']), None)
        if existing_booking:
            return jsonify({
                'message': 'Booking notification already exists',
                'notification_id': existing_booking['id'],
                'status': 'duplicate'
            }), 200
        
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
            'status': 'received',
            'crm_status': 'new'  # CRM-specific status
        }
        
        bookings_storage.append(notification)
        
        # Cache event and facilitator info
        events_cache[str(data['event']['id'])] = data['event']
        if 'facilitator' in data:
            facilitators_cache[str(data['facilitator_id'])] = data['facilitator']
        
        # Save to file for persistence
        save_data_to_file()
        
        # Log the notification
        print(f"📨 [CRM] New booking notification received:")
        print(f"   Booking ID: {data['booking_id']}")
        print(f"   User: {data['user']['name']} ({data['user']['email']})")
        print(f"   Event: {data['event']['title']} ({data['event']['type']})")
        print(f"   Facilitator ID: {data['facilitator_id']}")
        
        return jsonify({
            'message': 'Booking notification received successfully',
            'notification_id': notification['id'],
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Error in notify endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/bookings', methods=['GET'])
def get_all_bookings():
    """Get all received booking notifications with optional filtering"""
    if not authenticate_request():
        return jsonify({'error': 'Unauthorized', 'message': 'Valid Bearer token required'}), 401
    
    try:
        # Query parameters for filtering
        facilitator_id = request.args.get('facilitator_id', type=int)
        event_id = request.args.get('event_id', type=int)
        user_id = request.args.get('user_id', type=int)
        status = request.args.get('status')
        crm_status = request.args.get('crm_status')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 per page
        
        # Filter bookings
        filtered_bookings = bookings_storage.copy()
        
        if facilitator_id:
            filtered_bookings = [b for b in filtered_bookings if b['facilitator_id'] == facilitator_id]
        
        if event_id:
            filtered_bookings = [b for b in filtered_bookings if b['event']['id'] == event_id]
        
        if user_id:
            filtered_bookings = [b for b in filtered_bookings if b['user']['id'] == user_id]
        
        if status:
            filtered_bookings = [b for b in filtered_bookings if b['status'] == status]
        
        if crm_status:
            filtered_bookings = [b for b in filtered_bookings if b.get('crm_status') == crm_status]
        
        # Sort by received date (newest first)
        filtered_bookings.sort(key=lambda x: x['received_at'], reverse=True)
        
        # Pagination
        total = len(filtered_bookings)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_bookings = filtered_bookings[start:end]
        
        return jsonify({
            'bookings': paginated_bookings,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 0,
                'has_next': end < total,
                'has_prev': page > 1
            },
            'filters_applied': {
                'facilitator_id': facilitator_id,
                'event_id': event_id,
                'user_id': user_id,
                'status': status,
                'crm_status': crm_status
            },
            'summary': {
                'total_notifications': len(bookings_storage),
                'filtered_results': total
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error in get_all_bookings: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/facilitators/<int:facilitator_id>/bookings', methods=['GET'])
def get_facilitator_bookings(facilitator_id):
    """Get all bookings for a specific facilitator"""
    if not authenticate_request():
        return jsonify({'error': 'Unauthorized', 'message': 'Valid Bearer token required'}), 401
    
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        event_type = request.args.get('event_type')
        crm_status = request.args.get('crm_status')
        
        # Filter bookings for this facilitator
        facilitator_bookings = [b for b in bookings_storage if b['facilitator_id'] == facilitator_id]
        
        if not facilitator_bookings:
            return jsonify({
                'facilitator_id': facilitator_id,
                'bookings': [],
                'statistics': {
                    'total_bookings': 0,
                    'session_bookings': 0,
                    'retreat_bookings': 0,
                    'recent_bookings': 0,
                    'unique_users': 0
                },
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0,
                    'has_next': False,
                    'has_prev': False
                },
                'message': f'No bookings found for facilitator {facilitator_id}'
            }), 200
        
        # Additional filtering
        if status:
            facilitator_bookings = [b for b in facilitator_bookings if b['status'] == status]
        
        if event_type:
            facilitator_bookings = [b for b in facilitator_bookings if b['event']['type'] == event_type]
        
        if crm_status:
            facilitator_bookings = [b for b in facilitator_bookings if b.get('crm_status') == crm_status]
        
        # Sort by booking date (newest first)
        facilitator_bookings.sort(key=lambda x: x['received_at'], reverse=True)
        
        # Pagination
        total = len(facilitator_bookings)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_bookings = facilitator_bookings[start:end]
        
        # Calculate statistics
        all_facilitator_bookings = [b for b in bookings_storage if b['facilitator_id'] == facilitator_id]
        
        # Recent bookings (last 7 days)
        seven_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_bookings = []
        for booking in all_facilitator_bookings:
            try:
                booking_date = datetime.fromisoformat(booking['received_at'].replace('Z', '+00:00'))
                if booking_date.replace(tzinfo=None) >= seven_days_ago:
                    recent_bookings.append(booking)
            except:
                continue
        
        stats = {
            'total_bookings': len(all_facilitator_bookings),
            'session_bookings': len([b for b in all_facilitator_bookings if b['event']['type'] == 'session']),
            'retreat_bookings': len([b for b in all_facilitator_bookings if b['event']['type'] == 'retreat']),
            'recent_bookings': len(recent_bookings),
            'unique_users': len(set(b['user']['id'] for b in all_facilitator_bookings)),
            'unique_events': len(set(b['event']['id'] for b in all_facilitator_bookings))
        }
        
        return jsonify({
            'facilitator_id': facilitator_id,
            'bookings': paginated_bookings,
            'statistics': stats,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 0,
                'has_next': end < total,
                'has_prev': page > 1
            },
            'filters_applied': {
                'status': status,
                'event_type': event_type,
                'crm_status': crm_status
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error in get_facilitator_bookings: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/facilitators/<int:facilitator_id>/dashboard', methods=['GET'])
def get_facilitator_dashboard(facilitator_id):
    """Get dashboard data for a specific facilitator"""
    if not authenticate_request():
        return jsonify({'error': 'Unauthorized', 'message': 'Valid Bearer token required'}), 401
    
    try:
        # Get all bookings for this facilitator
        facilitator_bookings = [b for b in bookings_storage if b['facilitator_id'] == facilitator_id]
        
        if not facilitator_bookings:
            return jsonify({
                'facilitator_id': facilitator_id,
                'summary': {
                    'total_bookings': 0,
                    'session_bookings': 0,
                    'retreat_bookings': 0,
                    'recent_bookings_count': 0,
                    'unique_events': 0,
                    'unique_users': 0
                },
                'popular_events': [],
                'recent_bookings': [],
                'booking_trends': {
                    'sessions_vs_retreats': {
                        'sessions': 0,
                        'retreats': 0
                    }
                },
                'message': f'No bookings found for facilitator {facilitator_id}',
                'generated_at': datetime.utcnow().isoformat()
            }), 200
        
        # Calculate dashboard statistics
        total_bookings = len(facilitator_bookings)
        
        # Group by event type
        session_bookings = [b for b in facilitator_bookings if b['event']['type'] == 'session']
        retreat_bookings = [b for b in facilitator_bookings if b['event']['type'] == 'retreat']
        
        # Recent bookings (last 7 days)
        seven_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_bookings = []
        for booking in facilitator_bookings:
            try:
                booking_date = datetime.fromisoformat(booking['received_at'].replace('Z', '+00:00'))
                if booking_date.replace(tzinfo=None) >= seven_days_ago:
                    recent_bookings.append(booking)
            except:
                continue
        
        # Unique events and users
        unique_events = len(set(b['event']['id'] for b in facilitator_bookings))
        unique_users = len(set(b['user']['id'] for b in facilitator_bookings))
        
        # Popular events (most booked)
        event_counts = {}
        for booking in facilitator_bookings:
            event_id = booking['event']['id']
            event_title = booking['event']['title']
            if event_id not in event_counts:
                event_counts[event_id] = {
                    'event_id': event_id,
                    'event_title': event_title,
                    'event_type': booking['event']['type'],
                    'booking_count': 0
                }
            event_counts[event_id]['booking_count'] += 1
        
        popular_events = sorted(event_counts.values(), key=lambda x: x['booking_count'], reverse=True)[:5]
        
        # Recent bookings details (last 10)
        recent_bookings_details = sorted(recent_bookings, key=lambda x: x['received_at'], reverse=True)[:10]
        
        dashboard_data = {
            'facilitator_id': facilitator_id,
            'summary': {
                'total_bookings': total_bookings,
                'session_bookings': len(session_bookings),
                'retreat_bookings': len(retreat_bookings),
                'recent_bookings_count': len(recent_bookings),
                'unique_events': unique_events,
                'unique_users': unique_users
            },
            'popular_events': popular_events,
            'recent_bookings': recent_bookings_details,
            'booking_trends': {
                'sessions_vs_retreats': {
                    'sessions': len(session_bookings),
                    'retreats': len(retreat_bookings)
                }
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        print(f"❌ Error in get_facilitator_dashboard: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_specific_booking(booking_id):
    """Get specific booking notification by booking ID"""
    if not authenticate_request():
        return jsonify({'error': 'Unauthorized', 'message': 'Valid Bearer token required'}), 401
    
    try:
        booking = next((b for b in bookings_storage if b['booking_id'] == booking_id), None)
        
        if not booking:
            return jsonify({
                'error': 'Booking not found',
                'booking_id': booking_id,
                'message': f'No booking notification found with ID {booking_id}'
            }), 404
        
        return jsonify({
            'booking': booking
        }), 200
        
    except Exception as e:
        print(f"❌ Error in get_specific_booking: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/bookings/<int:booking_id>/status', methods=['PUT'])
def update_booking_status(booking_id):
    """Update CRM status of a booking"""
    if not authenticate_request():
        return jsonify({'error': 'Unauthorized', 'message': 'Valid Bearer token required'}), 401
    
    try:
        data = request.get_json()
        if not data or 'crm_status' not in data:
            return jsonify({
                'error': 'Missing crm_status field',
                'message': 'Request body must contain crm_status field'
            }), 400
        
        valid_statuses = ['new', 'reviewed', 'contacted', 'confirmed', 'completed']
        crm_status = data['crm_status']
        
        if crm_status not in valid_statuses:
            return jsonify({
                'error': 'Invalid crm_status',
                'message': f'crm_status must be one of: {valid_statuses}'
            }), 400
        
        # Find and update booking
        booking = next((b for b in bookings_storage if b['booking_id'] == booking_id), None)
        
        if not booking:
            return jsonify({
                'error': 'Booking not found',
                'booking_id': booking_id
            }), 404
        
        old_status = booking.get('crm_status', 'new')
        booking['crm_status'] = crm_status
        booking['crm_updated_at'] = datetime.utcnow().isoformat()
        booking['crm_notes'] = data.get('notes', '')
        
        # Save to file
        save_data_to_file()
        
        return jsonify({
            'message': 'Booking status updated successfully',
            'booking_id': booking_id,
            'old_status': old_status,
            'new_status': crm_status,
            'updated_at': booking['crm_updated_at']
        }), 200
        
    except Exception as e:
        print(f"❌ Error in update_booking_status: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CRM Notification Service',
        'port': 8003,
        'timestamp': datetime.utcnow().isoformat(),
        'notifications_received': len(bookings_storage),
        'unique_facilitators': len(set(b['facilitator_id'] for b in bookings_storage)),
        'unique_events': len(events_cache),
        'endpoints': [
            '/health',
            '/api/notify',
            '/api/bookings',
            '/api/facilitators/{id}/bookings',
            '/api/facilitators/{id}/dashboard',
            '/api/bookings/{id}',
            '/api/bookings/{id}/status'
        ]
    }), 200


if __name__ == '__main__':
    print("🚀 Starting CRM Notification Service...")
    print(f"🔑 Bearer Token: {BEARER_TOKEN}")
    
    # Load existing data
    load_data_from_file()
    
    print("🌐 CRM Service starting on http://0.0.0.0:8003")
    print("📋 Available endpoints:")
    print("   GET  /health")
    print("   POST /api/notify")
    print("   GET  /api/bookings")
    print("   GET  /api/facilitators/{id}/bookings")
    print("   GET  /api/facilitators/{id}/dashboard")
    print("   GET  /api/bookings/{id}")
    print("   PUT  /api/bookings/{id}/status")
    
    try:
        app.run(host="0.0.0.0", debug=True, port=8003, use_reloader=False)
    except Exception as e:
        print(f"❌ Failed to start CRM service: {e}")
        sys.exit(1)
