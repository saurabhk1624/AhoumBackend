from extensions import db
from datetime import datetime

class Facilitator(db.Model):
    __tablename__ = 'facilitators'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text)
    specialization = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)


    # Relationships
    users=db.relationship('User', backref='facilitator_id', lazy=True)
    events = db.relationship('Event', backref='facilitator', lazy=True)
    

    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.users.email,
            'first_name': self.users.first_name,
            'last_name': self.users.last_name,
            'phone': self.users.phone,
            'bio': self.bio,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'is_active': self.users.is_active,
        }
    
    @property
    def full_name(self):
        return f"{self.users.first_name} {self.users.last_name}"
    
    def __repr__(self):
        return f'<Facilitator {self.full_name}>'
