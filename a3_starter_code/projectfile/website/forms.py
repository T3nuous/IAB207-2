from flask_wtf import FlaskForm
from wtforms.fields import (StringField, PasswordField, TextAreaField,
                            IntegerField, DateTimeField, SubmitField)
from wtforms.validators import (InputRequired, Length, Email,
                                EqualTo, NumberRange, Regexp)
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        InputRequired(), Email('Please enter a valid email')
    ])
    password = PasswordField('Password', validators=[
        InputRequired('Enter your password')
    ])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        InputRequired('Enter your first name')
    ])
    surname = StringField('Surname', validators=[
        InputRequired('Enter your surname')
    ])
    email = StringField('Email Address', validators=[
        InputRequired('Enter your email'), Email('Enter a valid email')
    ])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=6)
    ])
    confirm = PasswordField('Confirm Password', validators=[
        InputRequired(), EqualTo('password', 'Passwords must match')
    ])
    submit = SubmitField('Register')

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[
        InputRequired(), Length(max=100)
    ])
    date_time = DateTimeField(
        'Date & Time',
        format='%Y-%m-%d %H:%M',
        validators=[InputRequired()]
    )
    location = StringField('Location', validators=[
        InputRequired(), Length(max=200)
    ])
    total_tickets = IntegerField('Total Tickets', validators=[
        InputRequired(), NumberRange(min=1)
    ])
    submit = SubmitField('Create Event')

class BookingForm(FlaskForm):
    quantity = IntegerField('Number of Tickets', validators=[
        InputRequired('Enter number of tickets'),
        NumberRange(min=1, message='Must book at least one ticket')
    ])
    submit = SubmitField('Book Tickets')

class CommentForm(FlaskForm):
    body = TextAreaField('Your Comment', validators=[
        InputRequired(), Length(max=500)
    ])
    submit = SubmitField('Post Comment')

# Form for updating profile information
class UpdateProfileForm(FlaskForm):
    email = StringField(
        'Email Address',
        render_kw={'readonly': True}
    )
    phone = StringField(
        'Phone Number',
        validators=[
            InputRequired('Enter your phone number'),
            Regexp(
                r'^\+?[\d\s\-]{7,20}$',
                message='Enter a valid phone number'
            )
        ]
    )
    address = StringField(
        'Address',
        validators=[
            InputRequired('Enter your address'),
            Length(max=200)
        ]
    )
    current_password = PasswordField('Current Password')  # only required if changing pw
    new_password     = PasswordField(
        'New Password',
        validators=[ Length(min=8, message='Password must be at least 8 characters') ]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[ EqualTo('new_password', message='Passwords must match') ]
    )
    submit = SubmitField('Update Profile')