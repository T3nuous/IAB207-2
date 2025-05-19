from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import (TextAreaField, SubmitField, StringField, PasswordField, 
                            DateField, TimeField, IntegerField, SelectField, DateTimeLocalField)
from wtforms.validators import (InputRequired, Length, Email, EqualTo, Regexp, 
                                NumberRange, ValidationError, Optional, URL)
from datetime import datetime 

# creates the login information
class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[InputRequired(), Email("Please enter a valid email")])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    firstName = StringField("First Name", validators=[InputRequired()])
    surname = StringField("Surname", validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired(), Email("Please enter a valid email")])
    mobileNumber = StringField("Mobile Number", validators=[InputRequired(), 
                                                              Length(min=7, max=20, message="Field must be between 7 and 20 digits."), 
                                                              Regexp(r'^\+?[0-9\s\-()]*$', message="Please only input valid phone characters.")]) 
    streetAddress = StringField("Street Address",  validators=[InputRequired(), Length(max=150)]) 
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match"),
                  Regexp(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$', message= "Password must be at least 8 characters and contain at least one uppercase letter, one symbol, and one number.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])
    submit = SubmitField("Register")

# Form for ticket types
class TicketTypeForm(FlaskForm):
    type_name = StringField('Ticket Type Name (e.g., General, VIP)', validators=[InputRequired(), Length(max=100)])
    price = IntegerField('Price ($)', validators=[InputRequired(), NumberRange(min=0, message="Price cannot be negative.")])
    quantity_available = IntegerField('Number of Tickets Available for this type', validators=[InputRequired(), NumberRange(min=1, message="Must be a positive number.")])
    description = TextAreaField('Ticket Description', validators=[Optional(), Length(max=500)])

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[InputRequired(), Length(max=120)])
    description = TextAreaField('Event Description', validators=[Optional(), Length(max=2000)])
    
    # Image Upload
    image = FileField('Event Image (JPG, PNG, JPEG only)', validators=[
        Optional(), 
        FileAllowed(['jpg', 'png', 'jpeg'], 'Only JPG, PNG, and JPEG images are allowed!')
    ])
    image_url = StringField('Or Image URL', validators=[Optional(), URL()])


    # Date/Time
    start_datetime = DateTimeLocalField('Start Date and Time', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])

    location = StringField('Location (e.g., Street Address, City)', validators=[InputRequired(), Length(max=100)])
    venue = StringField('Venue Name (e.g., Brisbane Convention Centre)', validators=[Optional(), Length(max=100)])
    
    category = SelectField('Category', coerce=int, validators=[InputRequired(message="Please select a category.")])
    
    genre = StringField('Genre (e.g., Hip Hop, Rock)', validators=[Optional(), Length(max=50)])
    age_limit = IntegerField('Age Limit (0 for all ages)', validators=[Optional(), NumberRange(min=0)])
    length = StringField('Event Length (e.g., 2 hours, Full Day)', validators=[Optional(), Length(max=50)])
    artist_info = TextAreaField('Artist Information', validators=[Optional(), Length(max=2000)])
    policies = TextAreaField('Event Policies', validators=[Optional(), Length(max=2000)])
    
    # Social media
    facebook = StringField('Facebook Link', validators=[Optional(), URL()])
    instagram = StringField('Instagram Link', validators=[Optional(), URL()])
    twitter = StringField('Twitter Link', validators=[Optional(), URL()])
    youtube = StringField('YouTube Link', validators=[Optional(), URL()])
    twitch = StringField('Twitch Link', validators=[Optional(), URL()])
    
    submit = SubmitField('Create Event')

    # Validation for Date/Time in future
    def validate_start_datetime(self, field):
        if field.data and field.data <= datetime.now():
            raise ValidationError("Event start date and time must be in the future.")


class TicketForm(FlaskForm): 
    general_price = IntegerField('General Ticket Price ($)', validators=[Optional(), NumberRange(min=0)])
    general_limit = IntegerField('General Ticket Limit', validators=[Optional(), NumberRange(min=1, message="Must be a positive number.")])

    # VIP Tickets (Optional)
    vip_price = IntegerField('VIP Ticket Price ($)', validators=[Optional(), NumberRange(min=0)])
    vip_limit = IntegerField('VIP Ticket Limit', validators=[Optional(), NumberRange(min=1, message="Must be a positive number if provided.")])
    
    # Balcony Tickets (Optional)
    balcony_price = IntegerField('Balcony Ticket Price ($)', validators=[Optional(), NumberRange(min=0)])
    balcony_limit = IntegerField('Balcony Ticket Limit', validators=[Optional(), NumberRange(min=1, message="Must be a positive number if provided.")])
    
    # Seat allocation
    front_row = StringField('Front Row Seats', validators=[Optional()])
    middle_row = StringField('Middle Row Seats', validators=[Optional()])
    back_row = StringField('Back Row Seats', validators=[Optional()])

# User comment
class CommentForm(FlaskForm):
    text = TextAreaField('Comment', [
        InputRequired('Please enter a comment'),
        Length(min=1, max=400, message='Comment must be between 1 and 400 characters')
    ])
    submit = SubmitField('Post Comment')

    def validate_text(self, field):
        if field.data and field.data.strip() == '': 
            raise ValidationError('Comment cannot be empty or just whitespace')
        
        if field.data and len(field.data.strip()) < 1: 
            raise ValidationError('Comment must contain at least one character')