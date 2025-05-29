from . import db
from datetime import datetime
from flask_login import UserMixin

# Defines the User data model for storing user information
# Inherits from db.Model for SQLAlchemy base model functionality
# Inherits from UserMixin for Flask-Login integration (e.g., is_authenticated)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the user
    firstName = db.Column(db.String(100), index=True, unique=False, nullable=False)  # User's first name, indexed for faster searches
    surname = db.Column(db.String(100), index=True, unique=False, nullable=False)  # User's surname, indexed
    email = db.Column(db.String(100), index=True, nullable=False, unique=True)  # User's email, must be unique
    mobileNumber = db.Column(db.String(15), index=True, nullable=False, unique=True)  # User's mobile number, must be unique
    streetAddress = db.Column(db.String(150), index=True, nullable=False)  # User's street address
    password_hash = db.Column(db.String(255), nullable=False)  # Hashed password for security
    role = db.Column(db.String(20), default='attendee')  # User role, defaults to 'attendee' (e.g., 'creator', 'admin')
    created_at = db.Column(db.DateTime, default=datetime.now)  # Timestamp for when the user was created
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # Timestamp for the last update
    
    # Relationships
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')
    events_created = db.relationship('Event', foreign_keys='Event.created_by', backref='creator_user', lazy='dynamic')
    
    # Provides a string representation of the User object
    def __repr__(self):
        return f"User: {self.firstName} {self.surname} ({self.role})"
    
# Defines the Genre data model for event genres
class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the genre
    name = db.Column(db.String(50), nullable=False, unique=True)  # Name of the genre (e.g., Rock, Jazz), must be unique
    description = db.Column(db.Text, nullable=True)  # Optional description of the genre
    image_filename = db.Column(db.String(255), nullable=True)  # Filename for an image representing the genre
    created_at = db.Column(db.DateTime, default=datetime.now)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # Last update timestamp
    
    # Relationship to the Event model
    # 'events' links to Event model, 'genre_info' is the backreference in Event
    events = db.relationship('Event', backref='genre_info', lazy='dynamic')
    
    def __repr__(self):
        return f"Genre: {self.name}"

# Defines the ticket_type data model for different kinds of tickets for an event
class ticket_type(db.Model):
    __tablename__ = 'ticket_type'
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the ticket type
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)  # Foreign key linking to the Event
    type_name = db.Column(db.String(100), nullable=False)  # Name of the ticket type (e.g., General, VIP)
    description = db.Column(db.Text, nullable=True) # Optional description for this ticket type
    price = db.Column(db.Float, nullable=False)  # Price of the ticket
    quantity_available = db.Column(db.Integer, nullable=False)  # Number of tickets available for this type
    created_at = db.Column(db.DateTime, default=datetime.now)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # Last update timestam
    
    def __repr__(self):
        return f"Ticket Type: {self.type_name} - ${self.price} ({self.quantity_available} available)"
    
# Defines the Event data model
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True) # Primary key for the event
    name = db.Column(db.String(120), index=True, nullable=False)  # Event name
    description = db.Column(db.Text, nullable=True)  # Optional detailed description of the event
    image_filename = db.Column(db.String(255), nullable=True)  # Filename of the event's image
    start_datetime = db.Column(db.DateTime, nullable=False)  # Combined start date and time for the event
    location = db.Column(db.String(100), nullable=False)  # General location of the event
    venue = db.Column(db.String(100), nullable=True)  # Specific venue name, optional
    
    # Music-specific fields    
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)  # Reference to Genre table
    artist_info = db.Column(db.Text, nullable=True) # Information about the artist(s)
    status = db.Column(db.String(20), default='Open', nullable=False)  # Current status of the event (e.g., Open, Cancelled)
    
    # Additional optional event details
    age_limit = db.Column(db.Integer, nullable=True) 
    length = db.Column(db.String(50), nullable=True)
    policies = db.Column(db.Text, nullable=True)
    
    # Social media links
    facebook = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Foreign key linking to the User who created the event
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships to other models
    # 'ticket_types' links to ticket_type model, 'event' is backreference in ticket_type
    # 'cascade' ensures that related ticket_types are deleted if the event is deleted
    ticket_types = db.relationship('ticket_type', backref='event', lazy='dynamic', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='event', lazy='dynamic', cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='event', lazy='dynamic', cascade="all, delete-orphan")

    # Property to calculate the current, dynamic status of the event
    @property
    def current_status(self):
        """
        Returns the current status of the event based on business logic:
        - If manually cancelled by creator -> 'Cancelled'
        - If start_datetime has passed -> 'Inactive' 
        - If sold out (no tickets available) -> 'Sold Out'
        - Otherwise -> 'Open'
        """
        # Check if manually cancelled
        if self.status == 'Cancelled':
            return 'Cancelled'
        
        # Check if manually completed
        if self.status == 'Completed':
            return 'Completed'
            
        # Check if event has expired (past the start date)
        if self.start_datetime and self.start_datetime < datetime.now():
            return 'Inactive'
        
        # Check if sold out (no tickets available)
        if self.ticket_types:
            total_available = sum(ticket.quantity_available for ticket in self.ticket_types)
            if total_available == 0:
                return 'Sold Out'
        
        # Default to open if none of the above conditions are met
        return 'Open'

    def __repr__(self):
        return f"Event: {self.name}"
    
# Defines the Comment data model for user comments on events
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True) # Primary key for comment
    text = db.Column(db.String(400), nullable=False)  # The content of the comment
    created_at = db.Column(db.DateTime, default=datetime.now)  # Timestamp of comment creation
    edited_at = db.Column(db.DateTime, nullable=True)  # Timestamp if the comment is edited
    is_edited = db.Column(db.Boolean, default=False)  # Flag to indicate if the comment has been edited
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Link to the User who made the comment
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False) # Link to the Event being commented on

    def __repr__(self):
        return f"Comment: {self.text[:50]}..." # Shows first 50 chars of comment text
    
# Defines the Order data model, representing a purchase transaction
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True) #Primary key for order
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who placed the order
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)# Event associated with the order (useful for context, though items link to ticket_types)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False) # Total amount for the order, using Numeric for precision
    order_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, confirmed, cancelled
    order_date = db.Column(db.DateTime, default=datetime.now) # Date the order was placed
    created_at = db.Column(db.DateTime, default=datetime.now) # Date the order was created
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now) # Date the order was edited
    
    # Relationships
    user = db.relationship('User', backref='orders') # Access user via order.user
    event = db.relationship('Event', backref='orders') # Access event via order.event
    # Cascade ensures order items are deleted if the order is deleted
    order_items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan")

    def __repr__(self):
        return f"Order #{self.id} - {self.order_status} (${self.total_amount})"

# Defines the OrderItem data model, representing individual items within an Order
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True) # Primary key for OrderItem
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_type.id'), nullable=False) # Link to the specific ticket_type purchased
    quantity = db.Column(db.Integer, nullable=False) # Number of tickets of this type in this order item
    unit_price = db.Column(db.Numeric(10, 2), nullable=False) # Price per unit at the time of purchase
    subtotal = db.Column(db.Numeric(10, 2), nullable=False) # Calculated as quantity * unit_price
    created_at = db.Column(db.DateTime, default=datetime.now) # Date of order creation
    
    # Relationships
    ticket_type = db.relationship('ticket_type', backref='order_items')

    # Cascade ensures order items are deleted if the order is deleted
    def __repr__(self):
        return f"OrderItem: {self.quantity}x {self.ticket_type.type_name if self.ticket_type else 'Unknown'}"

# Defines the Booking data model
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # User who made the booking
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False) # Event being booked
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)  # Link to order
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_type.id'), nullable=False) # Specific type of ticket booked
    quantity = db.Column(db.Integer, nullable=False) # Number of tickets booked
    total_price = db.Column(db.Numeric(10, 2), nullable=False)  # Better for currency
    booking_status = db.Column(db.String(20), default='confirmed', nullable=False)  # confirmed, cancelled, refunded
    booking_date = db.Column(db.DateTime, default=datetime.now) # When the booking was made
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

     # Relationships
    ticket_type_booked = db.relationship('ticket_type', backref='bookings') # Access ticket_type via booking.ticket_type_booked
    order = db.relationship('Order', backref='bookings')# Access order via booking.order

    def __repr__(self):
        return f"Booking #{self.id} - {self.quantity} tickets for event {self.event_id} ({self.booking_status})"
    
# Defines the event_status data model (historical status changes for an event)
class event_status(db.Model):
    __tablename__ = 'event_status'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id')) # Event this status change applies to
    status_date = db.Column(db.DateTime, default=datetime.now) # When this status was set
    status = db.Column(db.String(100), nullable=False) # The status value (e.g., 'Opened', 'Cancelled by User', 'Auto-Expired')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"Status: {self.status} on {self.status_date}"