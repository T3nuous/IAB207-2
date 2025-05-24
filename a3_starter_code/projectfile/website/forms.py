from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import (TextAreaField, SubmitField, StringField, PasswordField,                             DateField, TimeField, IntegerField, SelectField, DateTimeLocalField,                            DecimalField, HiddenField, FieldList, FormField, BooleanField)
from wtforms.validators import (InputRequired, Length, Email, EqualTo, Regexp, 
                                NumberRange, ValidationError, Optional, URL)
from wtforms.widgets import TextInput
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[InputRequired(), Email("Please enter a valid email")])
    password = PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    firstName = StringField("First Name", validators=[InputRequired(), Length(max=100)])
    surname = StringField("Surname", validators=[InputRequired(), Length(max=100)])
    email = StringField("Email Address", validators=[InputRequired(), Email("Please enter a valid email"), Length(max=100)])
    mobileNumber = StringField("Mobile Number", validators=[
        InputRequired(), 
        Length(min=7, max=15, message="Field must be between 7 and 15 characters."), 
        Regexp(r'^\+?[0-9\s\-()]*$', message="Please only input valid phone characters.")
    ]) 
    streetAddress = StringField("Street Address", validators=[InputRequired(), Length(max=150)]) 
    password = PasswordField("Password", validators=[
        InputRequired(),
        EqualTo('confirm', message="Passwords should match"),
        Regexp(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$', 
               message="Password must be at least 8 characters and contain at least one uppercase letter, one symbol, and one number.")
    ])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])
    submit = SubmitField("Register")

class TicketTypeForm(FlaskForm):
    type_name = StringField('Ticket Type Name (e.g., General, VIP)', validators=[InputRequired(), Length(max=100)])
    price = DecimalField('Price ($)', validators=[InputRequired(), NumberRange(min=0, message="Price cannot be negative.")], places=2)
    quantity_available = IntegerField('Number of Tickets Available', validators=[InputRequired(), NumberRange(min=1, message="Must be a positive number.")])
    description = TextAreaField('Ticket Description', validators=[Optional(), Length(max=500)])

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[InputRequired(message="Please name your event."), Length(max=120)])
    description = TextAreaField('Event Description', validators=[Optional(), Length(max=2000)])
    image = FileField('Event Image (JPG, PNG, JPEG only)', validators=[
        Optional(), 
        FileAllowed(['jpg', 'png', 'jpeg'], 'Only JPG, PNG, and JPEG images are allowed!')
    ])
    image_url = StringField('Or Image URL', validators=[Optional(), URL()])
    start_datetime = DateTimeLocalField('Start Date and Time', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    location = StringField('Location (e.g., Street Address, City)', validators=[InputRequired(), Length(max=100)])
    venue = StringField('Venue Name (e.g., Brisbane Convention Centre)', validators=[Optional(), Length(max=100)])
    category = SelectField('Category', coerce=int, validators=[InputRequired(message="Please select a category.")])
    
    # Music-specific fields    
    genre = StringField('Genre (e.g., Hip Hop, Rock, Pop)', validators=[Optional(), Length(max=50)])    
    artist_info = TextAreaField('Artist Information', validators=[Optional(), Length(max=2000)])
    
    # Event details
    age_limit = IntegerField('Age Limit (0 for all ages)', validators=[Optional(), NumberRange(min=0, max=99)])
    length = StringField('Event Length (e.g., 2 hours, Full Day)', validators=[Optional(), Length(max=50)])
    policies = TextAreaField('Event Policies', validators=[Optional(), Length(max=2000)])
    
    # Social media links
    facebook = StringField('Facebook Link', validators=[Optional(), URL()])
    instagram = StringField('Instagram Link', validators=[Optional(), URL()])
    twitter = StringField('Twitter Link', validators=[Optional(), URL()])
    
    submit = SubmitField('Create Event')

    def validate_start_datetime(self, field):
        if field.data and field.data <= datetime.now():
            raise ValidationError("Event start date and time must be in the future.")

class TicketForm(FlaskForm): 
    """Form for creating multiple ticket types for an event"""
    general_price = DecimalField('General Ticket Price ($)', validators=[Optional(), NumberRange(min=0, message="Price cannot be negative.")], places=2)
    general_quantity = IntegerField('General Ticket Quantity', validators=[Optional(), NumberRange(min=1, message="Must be a positive number.")])
    general_description = TextAreaField('General Ticket Description', validators=[Optional(), Length(max=500)])
    
    vip_price = DecimalField('VIP Ticket Price ($)', validators=[Optional(), NumberRange(min=0, message="Price cannot be negative.")], places=2)
    vip_quantity = IntegerField('VIP Ticket Quantity', validators=[Optional(), NumberRange(min=1, message="Must be a positive number.")])
    vip_description = TextAreaField('VIP Ticket Description', validators=[Optional(), Length(max=500)])

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        
        validation_passed = True
        
        # At least one ticket type must be provided
        if (not self.general_price.data and not self.vip_price.data):
            self.general_price.errors.append("At least one ticket type must be provided.")
            validation_passed = False
            
        # If price is provided, quantity must be provided too
        if self.general_price.data and not self.general_quantity.data:
            self.general_quantity.errors.append("Quantity is required when price is specified.")
            validation_passed = False
            
        if self.vip_price.data and not self.vip_quantity.data:
            self.vip_quantity.errors.append("Quantity is required when price is specified.")
            validation_passed = False
             
        return validation_passed

class OrderItemForm(FlaskForm):
    """Form for individual items in an order"""
    ticket_type_id = HiddenField('Ticket Type ID', validators=[InputRequired()])
    quantity = IntegerField('Quantity', validators=[InputRequired(), NumberRange(min=1, max=10, message="Quantity must be between 1 and 10")])

class CartForm(FlaskForm):
    """Form for managing shopping cart/order"""
    event_id = HiddenField('Event ID', validators=[InputRequired()])
    items = FieldList(FormField(OrderItemForm), min_entries=0)
    submit = SubmitField('Add to Cart')

class CheckoutForm(FlaskForm):
    """Form for finalizing an order"""
    # User can review their order and add any special notes
    special_notes = TextAreaField('Special Notes or Requests', validators=[Optional(), Length(max=500)])
    agree_terms = BooleanField('I agree to the terms and conditions', validators=[InputRequired(message="You must agree to the terms and conditions")])
    submit = SubmitField('Complete Purchase')

class BookingSearchForm(FlaskForm):
    """Form for searching bookings in admin panel"""
    booking_id = IntegerField('Booking ID', validators=[Optional()])
    user_email = StringField('User Email', validators=[Optional(), Email()])
    event_name = StringField('Event Name', validators=[Optional(), Length(max=120)])
    booking_status = SelectField('Booking Status', choices=[
        ('', 'All Statuses'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded')
    ], validators=[Optional()])
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    submit = SubmitField('Search')

class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[
        InputRequired('Please enter a comment'),
        Length(min=1, max=400, message='Comment must be between 1 and 400 characters')
    ])
    submit = SubmitField('Post Comment')

    def validate_text(self, field):
        if field.data and field.data.strip() == '': 
            raise ValidationError('Comment cannot be empty or just whitespace')
        if field.data and len(field.data.strip()) < 1: 
            raise ValidationError('Comment must contain at least one character')

class EventStatusForm(FlaskForm):
    """Form for updating event status"""
    status = SelectField('Event Status', choices=[('Open', 'Open'),
                                                  ('Sold Out', 'Sold Out'),
                                                  ('Cancelled', 'Cancelled'),
                                                  ('Postponed', 'Postponed'),
                                                  ('Completed', 'Completed')], validators=[InputRequired()])
    reason = TextAreaField('Reason for Status Change', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Status')

class BookingForm(FlaskForm):
    """Simple form for booking tickets - handles CSRF and dynamic quantities"""
    submit = SubmitField('Proceed to Checkout')

class ChangePasswordForm(FlaskForm):
    """Form for changing user password"""
    current_password = PasswordField('Current Password', validators=[InputRequired('Please enter your current password')])
    new_password = PasswordField('New Password', validators=[
        InputRequired('Please enter a new password'),
        EqualTo('confirm_password', message="Passwords should match"),
        Regexp(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$', 
               message="Password must be at least 8 characters and contain at least one uppercase letter, one symbol, and one number.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[InputRequired('Please confirm your new password')])
    submit = SubmitField('Change Password')

class EditCommentForm(FlaskForm):
    """Form for editing existing comments"""
    text = TextAreaField('Edit Comment', validators=[
        InputRequired('Please enter a comment'),
        Length(min=1, max=400, message='Comment must be between 1 and 400 characters')
    ])
    submit = SubmitField('Update Comment')

    def validate_text(self, field):
        if field.data and field.data.strip() == '': 
            raise ValidationError('Comment cannot be empty or just whitespace')
        if field.data and len(field.data.strip()) < 1: 
            raise ValidationError('Comment must contain at least one character')