from flask import Blueprint, render_template, request, session, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Event, Booking, Order, OrderItem, User
from .forms import ChangePasswordForm, ProfileUpdateForm
from sqlalchemy import desc, text, func
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import check_password_hash, generate_password_hash
from . import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Filter out cancelled and inactive events - only show upcoming active events
    upcoming_events = Event.query.filter(
        Event.status.notin_(['Cancelled', 'Inactive']),
        Event.start_datetime > datetime.now()  # Only future events
    ).order_by(Event.start_datetime.asc()).all()
    
    # Get popular events based on ticket sales (including past events for popularity)
    popular_events_query = db.session.query(
        Event,
        func.sum(Booking.quantity).label('total_tickets_sold')
    ).join(
        Booking, Event.id == Booking.event_id
    ).filter(
        Booking.booking_status == 'confirmed',
        Event.status.notin_(['Cancelled', 'Inactive'])
    ).group_by(
        Event.id
    ).order_by(
        text('total_tickets_sold DESC')
    ).limit(3).all()
    
    # Extract just the Event objects from the query results
    popular_events = [result[0] for result in popular_events_query] if popular_events_query else []
    
    # If we don't have enough popular events with sales, fill with upcoming events
    if len(popular_events) < 3:
        remaining_count = 3 - len(popular_events)
        # Get upcoming events that aren't already in popular_events
        popular_event_ids = [event.id for event in popular_events]
        additional_events = [event for event in upcoming_events 
                           if event.id not in popular_event_ids][:remaining_count]
        popular_events.extend(additional_events)
    
    # Get recommended events (events with least ticket sales - need promotion)
    # Use LEFT JOIN to include events with no bookings (0 sales)
    recommended_events_query = db.session.query(
        Event,
        func.coalesce(func.sum(Booking.quantity), 0).label('total_tickets_sold')
    ).outerjoin(  # LEFT JOIN to include events with no bookings
        Booking, (Event.id == Booking.event_id) & (Booking.booking_status == 'confirmed')
    ).filter(
        Event.status.notin_(['Cancelled', 'Inactive']),
        Event.start_datetime > datetime.now()  # Only future events for recommendations
    ).group_by(
        Event.id
    ).order_by(
        text('total_tickets_sold ASC'),  # Ascending - events with 0 sales come first
        Event.created_at.desc()  # Then by newest for events with same sales
    ).limit(3).all()
    
    recommended_events = [result[0] for result in recommended_events_query] if recommended_events_query else []
    
    return render_template('index.html', 
                         events=upcoming_events, 
                         popular_events=popular_events,
                         recommended_events=recommended_events)

@main_bp.route('/booking-history')
@login_required
def booking_history():
    # Get only orders for the current user
    user_orders = (Order.query
                  .filter_by(user_id=current_user.id)
                  .join(Event)
                  .order_by(desc(Order.order_date))
                  .all())
    
    # Get events created by the current user
    user_created_events = (Event.query
                          .filter_by(created_by=current_user.id)
                          .order_by(desc(Event.created_at))
                          .all())
    
    # Organize order history for the template
    booking_history = []
    
    # Add orders only
    for order in user_orders:
        # Determine the display status based on event status
        if order.event.current_status == 'Cancelled':
            display_status = 'Event Cancelled'
        elif order.event.current_status == 'Inactive':
            display_status = 'Event Completed'
        else:
            display_status = order.order_status
            
        order_info = {
            'id': order.id,
            'type': 'order',
            'event': order.event,
            'booking_date': order.order_date,
            'status': display_status,
            'total_price': order.total_amount,
            'order_items': order.order_items
        }
        booking_history.append(order_info)
    
    # Organize created events data
    creation_history = []
    for event in user_created_events:
        # Calculate total bookings and revenue for this event
        total_bookings = sum(booking.quantity for booking in event.bookings if booking.booking_status == 'confirmed')
        total_revenue = sum(float(booking.total_price) for booking in event.bookings if booking.booking_status == 'confirmed')
        
        # Calculate available tickets
        total_available = sum(ticket.quantity_available for ticket in event.ticket_types)
        
        creation_info = {
                         'event': event,
                         'created_date': event.created_at,
                         'total_bookings': total_bookings,
                         'total_revenue': total_revenue,
                         'available_tickets': total_available,
                         'status': event.current_status
                         }
        creation_history.append(creation_info)
    
    return render_template('events/bookingHistory.html', 
                         booking_history=booking_history, 
                         creation_history=creation_history)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Comprehensive profile update page"""
    form = ProfileUpdateForm(original_mobile=current_user.mobileNumber)
    
    if form.validate_on_submit():
        try:
            # Verify current password first
            if not check_password_hash(current_user.password_hash, form.current_password.data):
                flash('Current password is incorrect.', 'danger')
                return render_template('auth/profile.html', form=form)
            
            # Track what's being updated
            updates = []
            
            # Update mobile number if changed
            if form.mobileNumber.data != current_user.mobileNumber:
                current_user.mobileNumber = form.mobileNumber.data
                updates.append('mobile number')
            
            # Update address if changed
            if form.streetAddress.data != current_user.streetAddress:
                current_user.streetAddress = form.streetAddress.data
                updates.append('address')
            
            # Update password if provided
            if form.new_password.data:
                current_user.password_hash = generate_password_hash(form.new_password.data)
                updates.append('password')
            
            # Update the updated_at timestamp
            current_user.updated_at = datetime.now()
            
            # Commit changes
            db.session.commit()
            
            # Provide specific feedback
            if updates:
                update_text = ', '.join(updates)
                flash(f'Your {update_text} {"has" if len(updates) == 1 else "have"} been successfully updated!', 'success')
            else:
                flash('No changes were made to your profile.', 'info')
                
            return redirect(url_for('main.profile'))
            
        except IntegrityError as e:
            db.session.rollback()
            if 'mobileNumber' in str(e):
                flash('This mobile number is already registered to another account.', 'danger')
            else:
                flash('An error occurred while updating your profile. Please try again.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}', 'danger')
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.firstName.data = current_user.firstName
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.mobileNumber.data = current_user.mobileNumber
        form.streetAddress.data = current_user.streetAddress
    
    return render_template('auth/profile.html', form=form)

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Legacy password change route - redirects to profile"""
    flash('Password changes are now handled in your profile page.', 'info')
    return redirect(url_for('main.profile'))

