from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField,DateField, TimeField, IntegerField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, NumberRange, ValidationError, Optional, URL
from datetime import datetime


# creates the login information
class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    firstName = StringField("First Name", validators=[InputRequired()])
    surname = StringField("Surname", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    mobileNumber = StringField("Mobile Number", validators=[InputRequired(), 
                                                              Length(min=10, max=10, message="Field must be 10 digits."),
                                                              Regexp(r'^\d+$', message="Please only input digits.")])
    streetAddress = StringField("Street Address",  validators=[InputRequired()])
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match"),
                  Regexp(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]+$', message= "Password must contain at least one uppercase letter, one symbol, and one number.")])
    confirm = PasswordField("Confirm Password")

    # submit button
    submit = SubmitField("Register")

class TicketForm(FlaskForm):
    general_price = IntegerField('General Ticket Price ($)', validators=[InputRequired()])
    general_limit = IntegerField('General Ticket Limit', validators=[InputRequired()])
    vip_price = IntegerField('VIP Ticket Price ($)', validators=[Optional()])
    vip_limit = IntegerField('VIP Ticket Limit', validators=[Optional()])
    balcony_price = IntegerField('Balcony Ticket Price ($)', validators=[Optional()])
    balcony_limit = IntegerField('Balcony Ticket Limit', validators=[Optional()])
    front_row = StringField('Front Row Seats', validators=[Optional()])
    middle_row = StringField('Middle Row Seats', validators=[Optional()])
    back_row = StringField('Back Row Seats', validators=[Optional()])



class EventForm(FlaskForm):
    # Concert Details
    name = StringField('Concert Name', validators=[InputRequired()])
    genre = StringField('Concert Genre', validators=[InputRequired()])
    age_limit = IntegerField('Age Limit', validators=[InputRequired(), NumberRange(min=0)])
    start_time = TimeField('Start Time (HH:MM)', format='%H:%M', validators=[InputRequired()])
    end_time = TimeField('End Time (HH:MM)', format='%H:%M', validators=[InputRequired()])
    length = StringField('Concert Length', validators=[InputRequired()])
    start_date = DateField('Event Start Date', format='%Y-%m-%d', validators=[InputRequired()])
    end_date = DateField('Event End Date', format='%Y-%m-%d', validators=[InputRequired()])
    venue = StringField('Venue', validators=[InputRequired()])
    artist_info = TextAreaField('Artist Info', validators=[InputRequired()])
    description = TextAreaField('Event Description', validators=[InputRequired()])
    policies = TextAreaField('Event Policies', validators=[InputRequired()])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    location = StringField('Location', validators=[InputRequired()])
    facebook = StringField('Facebook Link', validators=[Optional(), URL()])
    instagram = StringField('Instagram Link', validators=[Optional(), URL()])
    twitter = StringField('Twitter Link', validators=[Optional(), URL()])
    youtube = StringField('YouTube Link', validators=[Optional(), URL()])
    twitch = StringField('Twitch Link', validators=[Optional(), URL()])
    submit = SubmitField('Create Event')

    def validate_start_date(self, field):
        if field.data < datetime.today().date():
            raise ValidationError("Start date must be today or in the future.")
        
    def validate_end_date(self, field):
        if self.start_date.data and field.data < self.start_date.data:
            raise ValidationError("End date must be after start date.")
        
class CommentForm(FlaskForm):
  text = TextAreaField('Comment', [InputRequired()])
  submit = SubmitField('Create')