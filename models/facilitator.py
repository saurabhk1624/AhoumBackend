from app import db
from datetime import datetime

class Facilitator(db.Model):
    __tablename__ = 'facilitators'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    specialization = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    events = db.relationship('Event', backref='facilitator', lazy=True)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_facilitator_email', 'email'),
        db.Index('idx_facilitator_active', 'is_active'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'bio': self.bio,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Facilitator {self.full_name}>'
