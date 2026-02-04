from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seats = db.relationship('Seat', backref='event',
                            lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Event {self.title}>'


class Seat(db.Model):
    __tablename__ = 'seats'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey(
        'events.id'), nullable=False)
    row = db.Column(db.String(5), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    is_available = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('event_id', 'row', 'number', name='unique_seat'),
    )

    def __repr__(self):
        return f'<Seat {self.row}{self.number}>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(20), unique=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey(
        'events.id'), nullable=False)

    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=True)

    status = db.Column(db.String(50), default='pending')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    payment_id = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seats = db.relationship('BookedSeat', backref='booking',
                            lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.booking_reference}>'


class BookedSeat(db.Model):
    __tablename__ = 'booked_seats'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey(
        'bookings.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)

    def __repr__(self):
        return f'<BookedSeat booking={self.booking_id} seat={self.seat_id}>'
