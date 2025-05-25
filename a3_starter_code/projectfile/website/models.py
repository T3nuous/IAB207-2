from . import db
from datetime import datetime, timezone
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id            = db.Column(db.Integer, primary_key=True)     # unique user ID
    name          = db.Column(db.String(150), nullable=False)   # display name
    emailid       = db.Column(db.String(150), unique=True, nullable=False)  # login email
    password_hash = db.Column(db.String(255), nullable=False)   # bcrypt hash
    phone         = db.Column(db.String(20), nullable=True)     # user phone number
    address       = db.Column(db.String(200), nullable=True)    # user mailing address

    orders        = db.relationship('Order',   back_populates='user')
    comments      = db.relationship('Comment', back_populates='author')

class Event(db.Model):
    __tablename__ = 'event'
    id                = db.Column(db.Integer, primary_key=True)       # unique event ID
    name              = db.Column(db.String(100), nullable=False)
    date_time         = db.Column(db.DateTime(timezone=True), nullable=False)
    location          = db.Column(db.String(200), nullable=False)
    total_tickets     = db.Column(db.Integer, nullable=False, default=0)
    tickets_remaining = db.Column(db.Integer, nullable=False, default=0)
    status            = db.Column(db.String(20), nullable=False, default='Open')
    price             = db.Column(db.Numeric(8,2), nullable=False, default=0.00)  # price per ticket

    orders            = db.relationship('Order',   back_populates='event')
    comments          = db.relationship('Comment', back_populates='event')

class Order(db.Model):
    __tablename__ = 'order'
    id            = db.Column(db.Integer, primary_key=True)         # unique booking ID
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id      = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    quantity      = db.Column(db.Integer, nullable=False)           # tickets booked
    created_at    = db.Column(
                       db.DateTime(timezone=True),
                       default=lambda: datetime.now(timezone.utc)   # UTC timestamp
                    )
    status        = db.Column(db.String(20), nullable=False, default='Active')  # Active or Cancelled

    user          = db.relationship('User',  back_populates='orders')
    event         = db.relationship('Event', back_populates='orders')

    @property
    def total_price(self):
        return self.quantity * self.event.price  # compute total cost

class Comment(db.Model):
    __tablename__ = 'comment'
    id            = db.Column(db.Integer, primary_key=True)        # unique comment ID
    body          = db.Column(db.Text, nullable=False)             # comment content
    author_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id      = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    created_at    = db.Column(
                       db.DateTime(timezone=True),
                       default=lambda: datetime.now(timezone.utc)   # UTC timestamp
                    )

    author        = db.relationship('User',    back_populates='comments')
    event         = db.relationship('Event',   back_populates='comments')