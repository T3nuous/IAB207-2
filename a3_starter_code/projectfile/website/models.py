from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users' # good practice to specify table name
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), index=True, unique=False, nullable=False)
    surname = db.Column(db.String(100), index=True, unique=False, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False, unique=True)
    mobileNumber = db.Column(db.Integer, index=True, nullable=False, unique=True)
    streetAddress = db.Column(db.String(50), index=True, nullable=False)
	# password should never stored in the DB, an encrypted password is stored
	# the storage should be at least 255 chars long, depending on your hashing algorithm
    password_hash = db.Column(db.String(255), nullable=False)
    # relation to call user.comments and comment.created_by
    comments = db.relationship('Comment', backref='user')
    
    # string print method
    def __repr__(self):
        return f"Name: {self.name}"
    

class ticket_type(db.Model):
    __tablename__ = 'ticket_type'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    type_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # string print method
    def __repr__(self):
        return f"Name: {self.type_name}"

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

    # Foreign key
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    ticket_types = db.relationship('ticket_type', backref='event', lazy='dynamic')
    comments = db.relationship('Comment', backref='event', lazy='dynamic')
    orders = db.relationship('Order', backref='event', lazy='dynamic')

    def __repr__(self):
        return f"<Event {self.name}>"
    
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    # add the foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    # string print method
    def __repr__(self):
        return f"Comment: {self.text}"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    ticket_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Order {self.id} - User {self.user_id}>"
    
class ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # ??
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.now())
    
        # string print method
    def __repr__(self):
        return f"Name: {self.name}"
    

    
class event_category(db.Model):
    __tablename__ = 'event_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # string print method
    def __repr__(self):
        return f"Name: {self.name}"
    
class event_status(db.Model):
    __tablename__ = 'event_status'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    status_date = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.String(100), nullable=False)
    
    # string print method
    def __repr__(self):
        return f"Name: {self.name}"
    

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.now())
    
    # string print method
    def __repr__(self):
        return f"Name: {self.name}" 