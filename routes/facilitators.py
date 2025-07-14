from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.facilitator import Facilitator
from models.event import Event
from models.booking import Booking

facilitators_bp = Blueprint('facilitators', __name__)

@facilitators_bp.route('/', methods=['GET'])
@jwt_required()
def get_facilitators():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        facilitators = Facilitator.query.filter(
            Facilitator.is_active == True
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'facilitators': [facilitator.to_dict() for facilitator in facilitators.items],
            'pagination': {
                'page': facilitators.page,
                'pages': facilitators.pages,
                'per_page': facilitators.per_page,
                'total': facilitators.total,
                'has_next': facilitators.has_next,
                'has_prev': facilitators.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@facilitators_bp.route('/<int:facilitator_id>', methods=['GET'])
@jwt_required()
def get_facilitator(facilitator_id):
    try:
        facilitator = Facilitator.query.get(facilitator_id)
        
        if not facilitator:
            return jsonify({'error': 'Facilitator not found'}), 404
        
        return jsonify({
            'facilitator': facilitator.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@facilitators_bp.route('/<int:facilitator_id>/events', methods=['GET'])
@jwt_required()
def get_facilitator_events(facilitator_id):
    try:
        facilitator = Facilitator.query.get(facilitator_id)
        
        if not facilitator:
            return jsonify({'error': 'Facilitator not found'}), 404
        
        events = Event.query.filter_by(facilitator_id=facilitator_id).all()
        
        return jsonify({
            'events': [event.to_dict() for event in events]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
