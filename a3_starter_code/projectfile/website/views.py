from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from . import db
from .models import Event, Order, Comment
from .forms import EventForm, BookingForm, CommentForm

main_bp = Blueprint('main', __name__)  # create main blueprint

@main_bp.route('/')
def index():
    # list all events sorted by start time (shows Sold Out/status badges)
    events = Event.query.order_by(Event.date_time).all()
    return render_template('index.html', events=events)

@main_bp.route('/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    # display and process event creation form
    form = EventForm()
    if form.validate_on_submit():
        evt = Event(
            name=form.name.data,
            date_time=form.date_time.data,
            location=form.location.data,
            total_tickets=form.total_tickets.data,
            tickets_remaining=form.total_tickets.data  # set initial remaining
        )
        db.session.add(evt)
        db.session.commit()
        flash('Event created!', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_event.html', form=form)

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    # show event info with booking/comment forms
    event = Event.query.get_or_404(event_id)
    return render_template(
        'event_detail.html',
        event=event,
        booking_form=BookingForm(),
        comment_form=CommentForm()
    )

@main_bp.route('/event/<int:event_id>/book', methods=['POST'])
@login_required
def book_event(event_id):
    # handle ticket booking request
    form = BookingForm()
    if form.validate_on_submit():
        evt = Event.query.get_or_404(event_id)
        # prevent oversell
        if evt.tickets_remaining < form.quantity.data:
            flash('Not enough tickets left.', 'danger')
        else:
            evt.tickets_remaining -= form.quantity.data  # deduct tickets
            # auto-mark sold out
            if evt.tickets_remaining == 0:
                evt.status = 'Sold Out'
            order = Order(
                user_id=current_user.id,
                event_id=event_id,
                quantity=form.quantity.data
            )
            db.session.add(order)
            db.session.commit()
            flash('Booking successful!', 'success')
    return redirect(url_for('main.event_detail', event_id=event_id))

@main_bp.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
def post_comment(event_id):
    # handle new comment submission
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            author_id=current_user.id,
            event_id=event_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted.', 'success')
    return redirect(url_for('main.event_detail', event_id=event_id))

@main_bp.route('/bookings')
@login_required
def bookings():
    # show active bookings for current user
    orders = Order.query.filter_by(
        user_id=current_user.id,
        status='Active'
    ).all()
    return render_template('bookings.html', orders=orders)

@main_bp.route('/booking/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(order_id):
    # allow user to cancel their own booking
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)  # forbid cancelling others
    order.event.tickets_remaining += order.quantity      # refund tickets
    order.status = 'Cancelled'                           # mark booking cancelled
    db.session.commit()
    flash('Booking cancelled', 'success')
    return redirect(url_for('main.bookings'))

@main_bp.route('/booking/<int:order_id>')
@login_required
def booking_detail(order_id):
    # show full details of a single booking
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)  # forbid viewing others
    return render_template(
        'booking_detail.html',
        order=order,
        total_price=order.total_price
    )