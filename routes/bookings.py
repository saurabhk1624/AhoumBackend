from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import requests
from extensions import db
from models.booking import Booking, BookingStatus
from models.event import Event, EventStatus,EventType
from models.user import User
from config import Config


bookings_bp = Blueprint('bookings', __name__)

def notify_crm(booking_data):
    """Send booking notification to CRM service"""
    try:
        headers = {
            'Authorization': f'Bearer {Config.CRM_BEARER_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{Config.CRM_SERVICE_URL}/api/notify',
            json=booking_data,
            headers=headers,
            timeout=10,
            verify=False
        
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"CRM notification failed: {str(e)}")
        return False

@bookings_bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    # try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        event_id = data.get('event_id')
        notes = data.get('notes', '')
        
        if not event_id:
            return jsonify({'error': 'Event ID is required'}), 400
        
        # Get event
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 400
        
        if event.status != EventStatus.ACTIVE:
            return jsonify({'error': 'Event is not available for booking'}), 400
        
        if event.is_full:
            return jsonify({'error': 'Event is fully booked'}), 400
        
        if event.start_datetime <= datetime.utcnow():
            return jsonify({'error': 'Cannot book past events'}), 400
        
        # Check if user already booked this event
        existing_booking = Booking.query.filter_by(
            user_id=current_user_id,
            event_id=event_id
        ).first()
        
        if existing_booking:
            return jsonify({'error': 'You have already booked this event'}), 409
        
        # Create booking
        booking = Booking(
            user_id=current_user_id,
            event_id=event_id,
            notes=notes,
            status=BookingStatus.CONFIRMED.value
        )
        
        # Update event participant count
        event.current_participants += 1
        
        db.session.add(booking)
        db.session.commit()
        
        # Prepare CRM notification data
        user = User.query.get(current_user_id)
        crm_data = {
            'booking_id': booking.id,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}",
                'phone': user.phone
            },
            'event': {
                'id': event.id,
                'title': event.title,
                'type': EventType(event.event_type).name,
                'start_datetime': event.start_datetime.isoformat(),
                'location': event.location
            },
            'facilitator_id': event.facilitator_id,
            'booking_date': booking.booking_date.isoformat(),
            'notes': notes
        }
        
        # Send CRM notification (non-blocking)
        crm_notified = notify_crm(crm_data)
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict(),
            'crm_notified': crm_notified
        }), 201
        
    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({'error': str(e)}), 400

@bookings_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_bookings():
    # try:
        current_user_id = int(get_jwt_identity())
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        upcoming_only = request.args.get('upcoming', 'false').lower() == 'true'
        
        # Build query
        query = Booking.query.filter(Booking.user_id == current_user_id)
        
        if status:
            try:
                status_enum = BookingStatus(status).name
                query = query.filter(Booking.status == status_enum)
            except ValueError:
                return jsonify({'error': 'Invalid status'}), 400
        
        if upcoming_only:
            query = query.join(Event).filter(Event.start_datetime > datetime.utcnow())
        
        # Order by booking date (newest first)
        query = query.order_by(Booking.created_at.desc())
        
        # Paginate
        bookings = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings.items],
            'pagination': {
                'page': bookings.page,
                'pages': bookings.pages,
                'per_page': bookings.per_page,
                'total': bookings.total,
                'has_next': bookings.has_next,
                'has_prev': bookings.has_prev
            }
        }), 200
        
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 400

@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        booking = Booking.query.filter_by(
            id=booking_id,
            user_id=current_user_id
        ).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 400
        
        return jsonify({
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bookings_bp.route('/<int:booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        booking = Booking.query.filter_by(
            id=booking_id,
            user_id=current_user_id
        ).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 400
        
        if booking.status == BookingStatus.CANCELLED:
            return jsonify({'error': 'Booking is already cancelled'}), 400
        
        if booking.event.start_datetime <= datetime.utcnow():
            return jsonify({'error': 'Cannot cancel past events'}), 400
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        
        # Update event participant count
        booking.event.current_participants -= 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
