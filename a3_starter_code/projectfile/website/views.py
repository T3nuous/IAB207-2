from flask import Blueprint, render_template, request, session
from .models import Event

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@main_bp.route('/booking-history')
def booking_history():
    events = Event.query.all()  # Get all events for the booking history
    return render_template('events/bookingHistory.html', events=events)