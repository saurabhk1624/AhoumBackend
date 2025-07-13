from app import create_app, db
from models.facilitator import Facilitator
from models.event import Event, EventType, EventStatus
from datetime import datetime, timedelta
from decimal import Decimal

def seed_database():
    """Seed the database with sample data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing data (be careful in production!)
            print("🧹 Clearing existing data...")
            Event.query.delete()
            Facilitator.query.delete()
            db.session.commit()
            
            # Create facilitators
            print("👥 Creating facilitators...")
            facilitators = [
                Facilitator(
                    email='sarah.johnson@example.com',
                    first_name='Sarah',
                    last_name='Johnson',
                    phone='+1-555-0101',
                    bio='Certified yoga instructor with 10+ years of experience in mindfulness and meditation.',
                    specialization='Yoga & Meditation',
                    experience_years=10
                ),
                Facilitator(
                    email='mike.chen@example.com',
                    first_name='Mike',
                    last_name='Chen',
                    phone='+1-555-0102',
                    bio='Life coach specializing in personal development and stress management.',
                    specialization='Life Coaching',
                    experience_years=8
                ),
                Facilitator(
                    email='emma.davis@example.com',
                    first_name='Emma',
                    last_name='Davis',
                    phone='+1-555-0103',
                    bio='Wellness expert focused on holistic health and nutrition.',
                    specialization='Wellness & Nutrition',
                    experience_years=12
                ),
                Facilitator(
                    email='alex.rodriguez@example.com',
                    first_name='Alex',
                    last_name='Rodriguez',
                    phone='+1-555-0104',
                    bio='Mindfulness teacher and retreat leader with expertise in group facilitation.',
                    specialization='Mindfulness & Retreats',
                    experience_years=15
                )
            ]
            
            for facilitator in facilitators:
                db.session.add(facilitator)
            
            db.session.commit()
            print(f"✅ Created {len(facilitators)} facilitators")
            
            # Create events
            print("📅 Creating events...")
            now = datetime.utcnow()
            
            events = [
                # Sessions
                Event(
                    title='Morning Yoga Flow',
                    description='Start your day with energizing yoga poses and breathing exercises.',
                    event_type=EventType.SESSION,
                    facilitator_id=1,
                    start_datetime=now + timedelta(days=3, hours=8),
                    end_datetime=now + timedelta(days=3, hours=9, minutes=30),
                    location='Studio A, Wellness Center',
                    max_participants=15,
                    price=Decimal('35.00'),
                    requirements='Bring your own yoga mat'
                ),
                Event(
                    title='Stress Management Workshop',
                    description='Learn practical techniques to manage stress and improve work-life balance.',
                    event_type=EventType.SESSION,
                    facilitator_id=2,
                    start_datetime=now + timedelta(days=5, hours=18),
                    end_datetime=now + timedelta(days=5, hours=20),
                    location='Conference Room B',
                    max_participants=20,
                    price=Decimal('45.00'),
                    requirements='Notebook and pen recommended'
                ),
                Event(
                    title='Nutrition Basics Seminar',
                    description='Understanding macronutrients and building healthy eating habits.',
                    event_type=EventType.SESSION,
                    facilitator_id=3,
                    start_datetime=now + timedelta(days=7, hours=14),
                    end_datetime=now + timedelta(days=7, hours=16),
                    location='Health Center Auditorium',
                    max_participants=25,
                    price=Decimal('40.00'),
                    requirements='None'
                ),
                Event(
                    title='Mindfulness Meditation',
                    description='Guided meditation session for beginners and experienced practitioners.',
                    event_type=EventType.SESSION,
                    facilitator_id=4,
                    start_datetime=now + timedelta(days=2, hours=19),
                    end_datetime=now + timedelta(days=2, hours=20, minutes=30),
                    virtual_link='https://zoom.us/j/123456789',
                    max_participants=30,
                    price=Decimal('25.00'),
                    requirements='Quiet space and comfortable seating'
                ),
                
                # Retreats
                Event(
                    title='Weekend Wellness Retreat',
                    description='Two-day intensive retreat focusing on yoga, meditation, and healthy living.',
                    event_type=EventType.RETREAT,
                    facilitator_id=1,
                    start_datetime=now + timedelta(days=14, hours=9),
                    end_datetime=now + timedelta(days=16, hours=17),
                    location='Mountain View Retreat Center',
                    max_participants=12,
                    price=Decimal('299.00'),
                    requirements='All meals included, bring comfortable clothing'
                ),
                Event(
                    title='Digital Detox Retreat',
                    description='Disconnect from technology and reconnect with yourself in nature.',
                    event_type=EventType.RETREAT,
                    facilitator_id=4,
                    start_datetime=now + timedelta(days=21, hours=10),
                    end_datetime=now + timedelta(days=23, hours=16),
                    location='Forest Lake Retreat',
                    max_participants=8,
                    price=Decimal('450.00'),
                    requirements='No electronic devices allowed, accommodation included'
                ),
                Event(
                    title='Personal Development Intensive',
                    description='Three-day program for goal setting, habit formation, and life planning.',
                    event_type=EventType.RETREAT,
                    facilitator_id=2,
                    start_datetime=now + timedelta(days=28, hours=9),
                    end_datetime=now + timedelta(days=30, hours=18),
                    location='Downtown Conference Center',
                    max_participants=15,
                    price=Decimal('399.00'),
                    requirements='Workbook provided, bring journal'
                ),
                Event(
                    title='Holistic Health Workshop',
                    description='Comprehensive approach to wellness including nutrition, exercise, and mental health.',
                    event_type=EventType.SESSION,
                    facilitator_id=3,
                    start_datetime=now + timedelta(days=10, hours=10),
                    end_datetime=now + timedelta(days=10, hours=15),
                    location='Wellness Institute',
                    max_participants=18,
                    price=Decimal('85.00'),
                    requirements='Lunch included'
                )
            ]
            
            for event in events:
                db.session.add(event)
            
            db.session.commit()
            print(f"✅ Created {len(events)} events")
            
            print("\n🎉 Database seeded successfully!")
            print(f"📊 Summary:")
            print(f"   - Facilitators: {len(facilitators)}")
            print(f"   - Events: {len(events)}")
            
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    seed_database()
