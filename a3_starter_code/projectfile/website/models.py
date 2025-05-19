from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), index=True, unique=False, nullable=False)
    surname = db.Column(db.String(100), index=True, unique=False, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False, unique=True)
    mobileNumber = db.Column(db.Integer, index=True, nullable=False, unique=True)
    streetAddress = db.Column(db.String(50), index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='attendee')  # 'admin', 'creator', 'attendee'
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    # Relationships
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')
    events = db.relationship('Event', backref='creator', lazy='dynamic')
    
    def __repr__(self):
        return f"User: {self.firstName} {self.surname} ({self.role})"

class ticket_type(db.Model):
    __tablename__ = 'ticket_type'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    type_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    def __repr__(self):
        return f"Ticket Type: {self.type_name} - ${self.price} ({self.quantity_available} available)"

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    age_limit = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    length = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    artist_info = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    policies = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Open')
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    youtube = db.Column(db.String(255))
    twitch = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('event_category.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    # Foreign key
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    ticket_types = db.relationship('ticket_type', backref='event', lazy='dynamic')
    comments = db.relationship('Comment', backref='event', lazy='dynamic')
    bookings = db.relationship('Booking', backref='event', lazy='dynamic')
    status_history = db.relationship('event_status', backref='event', lazy='dynamic')

    def __repr__(self):
        return f"Event: {self.name}"

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    edited_at = db.Column(db.DateTime, nullable=True)
    is_edited = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __repr__(self):
        return f"Comment: {self.text[:50]}..."

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_type.id'))
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    # Relationship to ticket_type
    ticket_type = db.relationship('ticket_type', backref='bookings')

    def __repr__(self):
        return f"Booking #{self.id} - {self.quantity} tickets"

class event_category(db.Model):
    __tablename__ = 'event_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    # Relationship to events
    events = db.relationship('Event', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f"Category: {self.name}"

class event_status(db.Model):
    __tablename__ = 'event_status'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    status_date = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    def __repr__(self):
        return f"Status: {self.status} on {self.status_date}" 