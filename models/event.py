from extensions import db
from datetime import datetime
import enum
from sqlalchemy import Numeric
class EventType(enum.IntEnum):
    SESSION = 1
    RETREAT = 2

class EventStatus(enum.IntEnum):
    ACTIVE = 1
    CANCELLED = 2
    COMPLETED = 3

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,)
    event_type = db.Column(db.Enum(EventType), nullable=False)
    facilitator_id = db.Column(db.Integer, db.ForeignKey('facilitators.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    virtual_link = db.Column(db.String(400))
    max_participants = db.Column(db.Integer, default=10)
    current_participants = db.Column(db.Integer, default=0)
    price = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(EventStatus), default=EventStatus.ACTIVE)
    requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='event', lazy=True, cascade='all, delete-orphan')
    
    # Indexes for better query performance
    __table_args__ = (
        db.Index('idx_event_facilitator', 'facilitator_id'),
        db.Index('idx_event_start_datetime', 'start_datetime'),
        db.Index('idx_event_type', 'event_type'),
        db.Index('idx_event_status', 'status'),
    )
    
    @property
    def is_full(self):
        return self.current_participants >= self.max_participants
    
    @property
    def available_spots(self):
        return self.max_participants - self.current_participants
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type.value,
            'facilitator': self.facilitator.to_dict() if self.facilitator else None,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'location': self.location,
            'virtual_link': self.virtual_link,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'available_spots': self.available_spots,
            'price': float(self.price),
            'status': self.status.value,
            'requirements': self.requirements,
            'is_full': self.is_full,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Event {self.title}>'
