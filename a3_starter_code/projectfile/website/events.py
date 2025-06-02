from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort, session
from .models import Event, Comment, ticket_type, Order, OrderItem, Booking, User, Genre
from .forms import EventForm, TicketForm, CommentForm, CheckoutForm, BookingForm, EditCommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from decimal import Decimal
from datetime import datetime

eventbp = Blueprint('event', __name__, url_prefix='/events')

@eventbp.route('/<int:id>')
def details(id):
    '''
    show the event details and the comments
    '''
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    cform = CommentForm()
    comments = event.comments.order_by(Comment.created_at.desc()).all() # order the comments by the date they were created
    return render_template('events/eventDetails.html', event=event, form=cform, comments=comments)


@eventbp.route('/eventspage')
def allevents():
    '''
    show all the events
    '''
    # Get search text from query parameters (for user story 3.4)
    search_text = request.args.get('search', '').strip()
    genre_filter = request.args.get('genre', '')
    # Build base query
    query = Event.query

    if genre_filter:
        # Filter by genre name instead of genre_id
        genre = Genre.query.filter_by(name=genre_filter).first()
        if genre:
            query = query.filter_by(genre_id=genre.id)
        else:
            query = query.filter(False)  # No matching genre, return empty
    else:
        # No genre filter applied; keep base query
        pass

    # Apply search filter if provided
    if search_text:
        query = query.filter(
            (Event.name.ilike(f"%{search_text}%")) |
            (Event.description.ilike(f"%{search_text}%"))
        )

    # Execute query ordered by start datetime
    events = query.order_by(Event.start_datetime.asc()).all()

    genres = db.session.scalars(db.select(Genre)).all()

    return render_template(
        'events/allEvents.html',
        events=events,
        genres=genres,
        selected_genre=genre_filter,
        search_text=search_text
    )

def check_upload_file(uploaded_file_data):
    '''
    check the upload file
    '''
    if not uploaded_file_data or not uploaded_file_data.filename:
        return None
    
    filename = secure_filename(uploaded_file_data.filename)
    
    upload_folder_abs = os.path.join(current_app.root_path, 'static', 'img', 'events')
    
    if not os.path.exists(upload_folder_abs):
        os.makedirs(upload_folder_abs, exist_ok=True)
    
    upload_path_abs = os.path.join(upload_folder_abs, filename)
    
    try:
        uploaded_file_data.save(upload_path_abs)
        
        # Verify file was actually saved
        if os.path.exists(upload_path_abs):
            file_size = os.path.getsize(upload_path_abs)
        else:
            flash("Error: File was not saved to disk", "danger")
            return None
        
        db_upload_path = os.path.join('img', 'events', filename).replace(os.sep, '/')
        flash(f"Image uploaded successfully: {filename}", "success")
        return db_upload_path
    except Exception as e:
        current_app.logger.error(f"Failed to save uploaded file: {e}")
        flash(f"Error uploading image: {str(e)}", "danger")
        return None

@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    '''
    create a new event
    '''
    form = EventForm()
    ticketform = TicketForm() 
    
    # Load genres for the dropdown
    try:
        genres = db.session.scalars(db.select(Genre)).all()
        form.genre.choices = [(genre.id, genre.name) for genre in genres]
    except Exception as e:
        current_app.logger.error(f"Error loading genres for event creation: {e}")
        flash("Error loading page data. Please check genre setup.", "danger")
        form.genre.choices = [] 

    if request.method == 'POST':
        if form.validate() and ticketform.validate():
            image_filename_to_save = None
            if form.image.data and form.image.data.filename:
                image_filename_to_save = check_upload_file(form.image.data)
            elif form.image_url.data and form.image_url.data.strip():
                image_filename_to_save = form.image_url.data.strip()
            
            new_event = Event(
                name=form.name.data,
                description=form.description.data,
                image_filename=image_filename_to_save,
                start_datetime=form.start_datetime.data,
                location=form.location.data,
                venue=form.venue.data,
                genre_id=form.genre.data,
                created_by=current_user.id,
                status='Open', # status of the event set to open on default
                age_limit=form.age_limit.data,
                length=form.length.data,
                artist_info=form.artist_info.data,
                policies=form.policies.data,
                facebook=form.facebook.data,
                instagram=form.instagram.data,
                twitter=form.twitter.data
            )
            try:
                db.session.add(new_event)
                db.session.flush()
                if ticketform.general_price.data is not None and ticketform.general_quantity.data is not None:
                    general_ticket = ticket_type(
                        event_id=new_event.id, type_name='General Admission',
                        price=ticketform.general_price.data, quantity_available=ticketform.general_quantity.data)
                    db.session.add(general_ticket)
                if ticketform.vip_price.data is not None and ticketform.vip_quantity.data is not None:
                    vip_ticket = ticket_type(
                        event_id=new_event.id, type_name='VIP',
                        price=ticketform.vip_price.data, quantity_available=ticketform.vip_quantity.data)
                    db.session.add(vip_ticket)
                
                db.session.commit()
                flash(f'Event "{new_event.name}" created successfully!', 'success')
                return redirect(url_for('event.details', id=new_event.id))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating event: {e}")
                flash(f"Error creating event: {str(e)}", "danger")
    return render_template('events/eventCreation.html', form=form, ticketform=ticketform, title="Create New Event")

@eventbp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    '''
    edit an event
    '''
    event_to_edit = db.session.query(Event).filter_by(id=id).first_or_404()

    if event_to_edit.created_by != current_user.id:
        flash("You are not authorized to edit this event.", "danger")
        return redirect(url_for('event.details', id=id))

    # Initialize forms 
    form = EventForm()
    ticketform = TicketForm()
    
    if request.method == 'GET':
        # For GET requests, populate from existing event data (except file fields)
        form.name.data = event_to_edit.name
        form.description.data = event_to_edit.description
        form.start_datetime.data = event_to_edit.start_datetime
        form.location.data = event_to_edit.location
        form.venue.data = event_to_edit.venue
        form.age_limit.data = event_to_edit.age_limit
        form.length.data = event_to_edit.length
        form.artist_info.data = event_to_edit.artist_info
        form.policies.data = event_to_edit.policies
        form.facebook.data = event_to_edit.facebook
        form.instagram.data = event_to_edit.instagram
        form.twitter.data = event_to_edit.twitter
        
        # Populate image_url field if current image is a URL
        if event_to_edit.image_filename and event_to_edit.image_filename.startswith('http'):
            form.image_url.data = event_to_edit.image_filename

    # Load genres for the dropdown (for both GET and POST)
    try:
        genres = db.session.scalars(db.select(Genre)).all()
        form.genre.choices = [(genre.id, genre.name) for genre in genres]
    except Exception as e:
        current_app.logger.error(f"Error loading genres for event editing: {e}")
        flash("Error loading page data. Please check genre setup.", "danger")
        form.genre.choices = []
    
    # Set the current genre and populate ticket data for GET requests
    if request.method == 'GET':
        form.genre.data = event_to_edit.genre_id
        
        # Populate ticket form data from existing tickets
        general_t = event_to_edit.ticket_types.filter_by(type_name='General Admission').first()
        if general_t:
            ticketform.general_price.data = int(general_t.price) if general_t.price is not None else None
            # Calculate total quantity = available + sold
            general_sold = sum(booking.quantity for booking in general_t.bookings if booking.booking_status == 'confirmed')
            ticketform.general_quantity.data = general_t.quantity_available + general_sold
        
        vip_t = event_to_edit.ticket_types.filter_by(type_name='VIP').first()
        if vip_t:
            ticketform.vip_price.data = int(vip_t.price) if vip_t.price is not None else None
            # Calculate total quantity = available + sold
            vip_sold = sum(booking.quantity for booking in vip_t.bookings if booking.booking_status == 'confirmed')
            ticketform.vip_quantity.data = vip_t.quantity_available + vip_sold

    # Calculate ticket sales information for display in template
    ticket_sales_info = {}
    general_t = event_to_edit.ticket_types.filter_by(type_name='General Admission').first()
    if general_t:
        general_sold = sum(booking.quantity for booking in general_t.bookings if booking.booking_status == 'confirmed')
        ticket_sales_info['general_sold'] = general_sold
        ticket_sales_info['general_available'] = general_t.quantity_available
    else:
        ticket_sales_info['general_sold'] = 0
        ticket_sales_info['general_available'] = 0
    
    vip_t = event_to_edit.ticket_types.filter_by(type_name='VIP').first()
    if vip_t:
        vip_sold = sum(booking.quantity for booking in vip_t.bookings if booking.booking_status == 'confirmed')
        ticket_sales_info['vip_sold'] = vip_sold
        ticket_sales_info['vip_available'] = vip_t.quantity_available
    else:
        ticket_sales_info['vip_sold'] = 0
        ticket_sales_info['vip_available'] = 0

    if request.method == 'POST':
        if form.validate() and ticketform.validate():
            # Store the current image filename before populate_obj potentially overwrites it
            current_image_filename = event_to_edit.image_filename
            
            form.populate_obj(event_to_edit) 
            
            # Handle image upload - exactly like in creation function
            image_filename_to_save = current_image_filename  # Default to current image
            
            if form.image.data and form.image.data.filename:
                new_image_filename = check_upload_file(form.image.data)
                if new_image_filename:
                    image_filename_to_save = new_image_filename
            
            # Handle image URL (additional feature for edit)
            elif form.image_url.data and form.image_url.data.strip():
                image_filename_to_save = form.image_url.data.strip()
            
            # Set the final image filename
            event_to_edit.image_filename = image_filename_to_save
            
            ticket_types_to_update = {
                'General Admission': (ticketform.general_price.data, ticketform.general_quantity.data),
                'VIP': (ticketform.vip_price.data, ticketform.vip_quantity.data)
            }

            for type_name_key, (price_data, limit_data) in ticket_types_to_update.items():
                existing_ticket = event_to_edit.ticket_types.filter_by(type_name=type_name_key).first()
                if price_data is not None and limit_data is not None:
                    if existing_ticket:
                        # Calculate how many tickets have been sold for this ticket type
                        sold_tickets = sum(booking.quantity for booking in existing_ticket.bookings if booking.booking_status == 'confirmed')
                        
                        # Check if the new quantity is less than already sold tickets
                        if limit_data < sold_tickets:
                            flash(f"Cannot set {type_name_key} quantity to {limit_data}. {sold_tickets} tickets have already been sold.", "danger")
                            return render_template('events/editEvent.html', form=form, ticketform=ticketform, event_id=event_to_edit.id, event=event_to_edit, title=f"Edit Event: {event_to_edit.name}", ticket_sales_info=ticket_sales_info)
                        
                        existing_ticket.price = float(price_data) 
                        # New available quantity = new total quantity - sold tickets
                        existing_ticket.quantity_available = limit_data - sold_tickets
                    else:
                        new_ticket = ticket_type(
                            event_id=event_to_edit.id,
                            type_name=type_name_key,
                            price=float(price_data), 
                            quantity_available=limit_data
                        )
                        db.session.add(new_ticket)
                elif existing_ticket:
                    # Check if any tickets have been sold before deleting
                    sold_tickets = sum(booking.quantity for booking in existing_ticket.bookings if booking.booking_status == 'confirmed')
                    if sold_tickets > 0:
                        flash(f"Cannot remove {type_name_key} tickets. {sold_tickets} tickets have already been sold.", "danger")
                        return render_template('events/editEvent.html', form=form, ticketform=ticketform, event_id=event_to_edit.id, event=event_to_edit, title=f"Edit Event: {event_to_edit.name}", ticket_sales_info=ticket_sales_info)
                    db.session.delete(existing_ticket)
            try:
                db.session.commit()
                flash(f'Event "{event_to_edit.name}" updated successfully!', 'success')
                return redirect(url_for('event.details', id=event_to_edit.id))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating event: {e}")
                flash(f"Error updating event: {str(e)}", "danger")
    return render_template('events/editEvent.html', form=form, ticketform=ticketform, event_id=event_to_edit.id, event=event_to_edit, title=f"Edit Event: {event_to_edit.name}", ticket_sales_info=ticket_sales_info)

@eventbp.route('/<int:id>/cancel_confirm', methods=['GET'])
@login_required
def cancel_confirm(id):
    '''
    confirm to cancel an event
    '''
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    if event.created_by != current_user.id:
        flash("You are not authorized to cancel this event.", "danger")
        return redirect(url_for('event.details', id=id))
    if event.status == 'Cancelled':
        flash("This event has already been cancelled.", "info")
        return redirect(url_for('event.details', id=id))
    return render_template('events/cancel_confirm.html', event=event, csrf_token=generate_csrf)

@eventbp.route('/<int:id>/cancel_confirmed', methods=['POST'])
@login_required
def cancel_event_confirmed(id):
    '''
    cancel an event
    '''
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    if event.created_by != current_user.id:
        flash("You are not authorized to cancel this event.", "danger")
        return redirect(url_for('event.details', id=id))
    if event.status == 'Cancelled':
        flash("This event has already been cancelled.", "info")
        return redirect(url_for('event.details', id=id))
    try:
        event.status = 'Cancelled'
        db.session.commit()
        flash(f'The event "{event.name}" has been successfully cancelled.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling event: {e}")
        flash(f"Error cancelling event: {str(e)}", "danger")
    return redirect(url_for('event.details', id=id))

@eventbp.route('/<int:id>/comment', methods=['POST'])
@login_required
def comment(id):
    '''
    add a comment to an event
    '''
    form = CommentForm()
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        new_comment = Comment(text=form.text.data, event_id=event.id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been added successfully.', 'success')
    else:
        for field, errors_list in form.errors.items():
            for error in errors_list:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('event.details', id=id))

@eventbp.route('/<int:event_id>/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(event_id, comment_id):
    '''
    edit/update a comment
    '''
    comment = db.session.query(Comment).filter_by(id=comment_id).first_or_404()
    event = db.session.query(Event).filter_by(id=event_id).first_or_404()
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.id:
        flash('You can only edit your own comments.', 'danger')
        return redirect(url_for('event.details', id=event_id))
    
    form = EditCommentForm()
    
    if request.method == 'GET':
        form.text.data = comment.text
    
    if form.validate_on_submit():
        comment.text = form.text.data
        comment.edited_at = datetime.now()
        comment.is_edited = True
        db.session.commit()
        flash('Your comment has been updated successfully.', 'success')
        return redirect(url_for('event.details', id=event_id))
    
    return render_template('events/edit_comment.html', form=form, comment=comment, event=event)

@eventbp.route('/<int:event_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(event_id, comment_id):
    '''
    delete a comment
    '''
    comment = db.session.query(Comment).filter_by(id=comment_id).first_or_404()
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.id:
        flash('You can only delete your own comments.', 'danger')
        return redirect(url_for('event.details', id=event_id))
    
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted successfully.', 'success')
    return redirect(url_for('event.details', id=event_id))

# ===============================
# BOOKING SYSTEM ROUTES
# ===============================

@eventbp.route('/<int:id>/book', methods=['GET', 'POST'])
@login_required
def book_tickets(id):
    """Main booking page where users select ticket quantities"""
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    form = BookingForm()
    # Check if event is available for booking
    if event.current_status in ['Cancelled', 'Sold Out', 'Completed', 'Inactive']:
        flash(f"Sorry, this event is {event.current_status.lower()} and not available for booking.", "warning")
        return redirect(url_for('event.details', id=id))
    # Get available ticket types
    ticket_types = event.ticket_types.filter(ticket_type.quantity_available > 0).all()
    if not ticket_types:
        flash("Sorry, there are no tickets available for this event.", "warning")
        return redirect(url_for('event.details', id=id))
    if form.validate_on_submit():
        cart_items = []
        total_amount = Decimal('0.00') # Process each ticket type
        
        # use for loop to process each ticket type, get the quantity of the ticket type, and check if the quantity is valid
        for ticket in ticket_types:
            quantity_field = f'quantity_{ticket.id}'
            quantity = request.form.get(quantity_field, type=int)
            if quantity and quantity > 0:
                if quantity > ticket.quantity_available:
                    flash(f"Sorry, only {ticket.quantity_available} {ticket.type_name} tickets are available.", "danger")
                    return render_template('events/bookTickets.html', event=event, ticket_types=ticket_types, form=form)
            if quantity > 10:
                # Limit per transaction
                flash("Maximum 10 tickets per type per transaction.", "danger")
                return render_template('events/bookTickets.html', event=event, ticket_types=ticket_types, form=form)
            subtotal = Decimal(str(ticket.price)) * quantity
            cart_items.append({'ticket_type_id': ticket.id,
                                'ticket_type_name': ticket.type_name,
                                'price': Decimal(str(ticket.price)),
                                'quantity': quantity,
                                'subtotal': subtotal
                                })
            total_amount += subtotal
            
        # if the cart is empty, flash a message and return the booking page
        if not cart_items:
            flash("Please select at least one ticket to proceed.", "warning")
            return render_template('events/bookTickets.html', event=event, ticket_types=ticket_types, form=form)
            # Directly create the booking without payment processing
        try:
            # Create the order
            order = Order(
                user_id=current_user.id, 
                event_id=event.id, 
                total_amount=total_amount, 
                order_status='confirmed') # Directly confirmed for assignment
            db.session.add(order)
            db.session.flush()  # Get the order ID
            # Create order items and update ticket availability
            for item in cart_items:
                # Check ticket availability again
                ticket = db.session.query(ticket_type).filter_by(id=item['ticket_type_id']).first()
                if not ticket or ticket.quantity_available < item['quantity']:
                    raise ValueError(f"Insufficient tickets available for {item['ticket_type_name']}")
                # Create order item
                order_item = OrderItem(order_id=order.id, ticket_type_id=item['ticket_type_id'], quantity=item['quantity'], unit_price=item['price'], subtotal=item['subtotal'])
                db.session.add(order_item)
                # Update ticket availability
                ticket.quantity_available -= item['quantity']
                # Create individual booking records for each ticket
                booking = Booking(user_id=current_user.id, event_id=event.id, order_id=order.id, ticket_type_id=item['ticket_type_id'], quantity=item['quantity'], total_price=item['subtotal'], booking_status='confirmed')
                db.session.add(booking)
            # Check if event should be marked as sold out
            remaining_tickets = sum(t.quantity_available for t in event.ticket_types)
            if remaining_tickets == 0:
                event.status = 'Sold Out'
            db.session.commit()
            flash(f'🎉 Congratulations! Your booking for "{event.name}" has been confirmed!', 'success')
            return redirect(url_for('event.booking_confirmation', id=event.id, order_id=order.id))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
            return render_template('events/bookTickets.html', event=event, ticket_types=ticket_types, form=form)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Booking error: {e}")
            flash("Sorry, there was an error processing your booking. Please try again.", "danger")
            return render_template('events/bookTickets.html', event=event, ticket_types=ticket_types, form=form)
    return render_template('events/bookTickets.html', event=event, ticket_types=ticket_types, form=form)


@eventbp.route('/<int:id>/checkout', methods=['GET', 'POST'])
@login_required
def checkout(id):
    '''
    checkout page for reviewing and confirming the order
    '''
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    
    # Check if cart exists
    cart = session.get('cart')
    if not cart or cart.get('event_id') != event.id:
        flash("Your cart is empty or has expired. Please select tickets again.", "warning")
        return redirect(url_for('event.book_tickets', id=id))
    
    form = CheckoutForm()
    
    if form.validate_on_submit():
        try:
            # Start database transaction
            # Create the order
            order = Order(
                user_id=current_user.id,
                event_id=event.id,
                total_amount=Decimal(str(cart['total_amount'])),
                order_status='pending'
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID
            
            # Create order items and update ticket availability, use for loop to process each order item
            for item in cart['items']:
                # Check ticket availability again
                ticket = db.session.query(ticket_type).filter_by(id=item['ticket_type_id']).first()
                if not ticket or ticket.quantity_available < item['quantity']:
                    raise ValueError(f"Insufficient tickets available for {item['ticket_type_name']}")
                
                # Create order item
                order_item = OrderItem(
                    order_id=order.id,
                    ticket_type_id=item['ticket_type_id'],
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    subtotal=item['subtotal']
                )
                db.session.add(order_item)
                
                # Update ticket availability
                ticket.quantity_available -= item['quantity']
                
                # Create individual booking records for each ticket
                booking = Booking(
                    user_id=current_user.id,
                    event_id=event.id,
                    order_id=order.id,
                    ticket_type_id=item['ticket_type_id'],
                    quantity=item['quantity'],
                    total_price=item['subtotal'],
                    booking_status='confirmed'
                )
                db.session.add(booking)
            
            # Mark order as confirmed
            order.order_status = 'confirmed'
            
            # Check if event should be marked as sold out
            remaining_tickets = sum(t.quantity_available for t in event.ticket_types)
            if remaining_tickets == 0:
                event.status = 'Sold Out'
            
            db.session.commit()
            
            # Clear cart
            session.pop('cart', None)
            
            flash(f'🎉 Congratulations! Your booking for "{event.name}" has been confirmed!', 'success')
            return redirect(url_for('event.booking_confirmation', id=event.id, order_id=order.id))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
            return redirect(url_for('event.book_tickets', id=id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Booking error: {e}")
            flash("Sorry, there was an error processing your booking. Please try again.", "danger")
            return redirect(url_for('event.book_tickets', id=id))
    
    return render_template('events/checkout.html', event=event, cart=cart, form=form)


@eventbp.route('/<int:id>/booking-confirmation/<int:order_id>')
@login_required
def booking_confirmation(id, order_id):
    '''
    booking confirmation page
    '''
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    order = db.session.query(Order).filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Get order items with ticket details, use for loop to process each order item
    order_items = []
    for item in order.order_items:
        order_items.append({
            'ticket_type_name': item.ticket_type.type_name,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'subtotal': item.subtotal
        })
    
    return render_template('events/bookingConfirmation.html', 
                         event=event, 
                         order=order, 
                         order_items=order_items)


@eventbp.route('/cart/clear')
@login_required
def clear_cart():
    '''
    clear the shopping cart
    '''
    session.pop('cart', None)
    flash("Your cart has been cleared.", "info")
    return redirect(request.referrer or url_for('event.allevents'))