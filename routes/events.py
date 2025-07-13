from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_
from datetime import datetime
from app import db
from models.event import Event, EventType, EventStatus
from models.facilitator import Facilitator

events_bp = Blueprint('events', __name__)

@events_bp.route('/', methods=['GET'])
@jwt_required()
def get_events():
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        event_type = request.args.get('type')
        facilitator_id = request.args.get('facilitator_id', type=int)
        status = request.args.get('status', 'active')
        search = request.args.get('search')
        
        # Build query
        query = Event.query.filter(Event.status == EventStatus.ACTIVE)
        
        if event_type:
            try:
                event_type_enum = EventType(event_type)
                query = query.filter(Event.event_type == event_type_enum)
            except ValueError:
                return jsonify({'error': 'Invalid event type'}), 400
        
        if facilitator_id:
            query = query.filter(Event.facilitator_id == facilitator_id)
        
        if search:
            query = query.filter(
                or_(
                    Event.title.contains(search),
                    Event.description.contains(search)
                )
            )
        
        # Filter future events only
        query = query.filter(Event.start_datetime > datetime.utcnow())
        
        # Order by start date
        query = query.order_by(Event.start_datetime.asc())
        
        # Paginate
        events = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'events': [event.to_dict() for event in events.items],
            'pagination': {
                'page': events.page,
                'pages': events.pages,
                'per_page': events.per_page,
                'total': events.total,
                'has_next': events.has_next,
                'has_prev': events.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    try:
        event = Event.query.get(event_id)
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        return jsonify({
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/types', methods=['GET'])
@jwt_required()
def get_event_types():
    try:
        return jsonify({
            'event_types': [event_type.value for event_type in EventType]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
