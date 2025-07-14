from extensions import db
from datetime import datetime
import enum

class BookingStatus(enum.IntEnum):
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3
    COMPLETED = 4

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Integer, default=BookingStatus.PENDING)
    notes = db.Column(db.Text)
    payment_status = db.Column(db.String(20), default='pending')  # For future payment integration
    payment_id = db.Column(db.String(100))  # For future payment integration
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint and indexes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_booking'),
        db.Index('idx_booking_user', 'user_id'),
        db.Index('idx_booking_event', 'event_id'),
        db.Index('idx_booking_status', 'status'),
        db.Index('idx_booking_date', 'booking_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'event': self.event.to_dict() if self.event else None,
            'booking_date': self.booking_date.isoformat(),
            'status': BookingStatus(self.status).name,
            'notes': self.notes,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Booking {self.id}: User {self.user_id} -> Event {self.event_id}>'
