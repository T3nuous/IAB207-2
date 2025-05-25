from flask_wtf import FlaskForm
from wtforms.fields import (StringField, PasswordField, TextAreaField,
                            IntegerField, DateTimeField, SubmitField)
from wtforms.validators import (InputRequired, Length, Email,
                                EqualTo, NumberRange)
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