from flask import Blueprint, render_template, request, session, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Event, Booking, Order, OrderItem, User
from .forms import ChangePasswordForm, ProfileUpdateForm
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import check_password_hash, generate_password_hash
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@main_bp.route('/booking-history')
@login_required
def booking_history():
    # Get actual bookings for the current user
    # We'll get both individual bookings and orders with their events
    user_bookings = (Booking.query
                    .filter_by(user_id=current_user.id)
                    .join(Event)
                    .order_by(desc(Booking.booking_date))
                    .all())
    
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
    
    # Combine and organize booking data for the template
    booking_history = []
    
    # Add individual bookings
    for booking in user_bookings:
        booking_info = {
            'id': booking.id,
            'type': 'booking',
            'event': booking.event,
            'booking_date': booking.booking_date,
            'status': booking.booking_status,
            'quantity': booking.quantity,
            'total_price': booking.total_price,
            'ticket_type': booking.ticket_type_booked
        }
        booking_history.append(booking_info)
    
    # Add orders
    for order in user_orders:
        order_info = {
            'id': order.id,
            'type': 'order',
            'event': order.event,
            'booking_date': order.order_date,
            'status': order.order_status,
            'total_price': order.total_amount,
            'order_items': order.order_items
        }
        booking_history.append(order_info)
    
    # Sort all booking history by date (most recent first)
    booking_history.sort(key=lambda x: x['booking_date'], reverse=True)
    
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
            from datetime import datetime
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

# Test routes for error pages (remove in production)
@main_bp.route('/test-404')
def test_404():
    """Test route to trigger 404 error page"""
    abort(404)

@main_bp.route('/test-500')
def test_500():
    """Test route to trigger 500 error page"""
    # Intentionally cause a server error
    raise Exception("This is a test 500 error")