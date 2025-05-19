from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from .models import Event, Comment, ticket_type, event_category
from .forms import EventForm, TicketForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf

eventbp = Blueprint('event', __name__, url_prefix='/events')

@eventbp.route('/<int:id>')
def details(id):
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    cform = CommentForm()
    return render_template('events/eventDetails.html', event=event, form=cform)

def check_upload_file(uploaded_file_data):
    if not uploaded_file_data or not uploaded_file_data.filename:
        return None
    filename = secure_filename(uploaded_file_data.filename)
    upload_folder_abs = os.path.join(current_app.root_path, 'static', 'img', 'events')
    if not os.path.exists(upload_folder_abs):
        os.makedirs(upload_folder_abs, exist_ok=True)
    upload_path_abs = os.path.join(upload_folder_abs, filename)
    try:
        uploaded_file_data.save(upload_path_abs)
        db_upload_path = os.path.join('img', 'events', filename).replace(os.sep, '/')
        return db_upload_path
    except Exception as e:
        current_app.logger.error(f"Failed to save uploaded file: {e}")
        flash(f"Error uploading image: {str(e)}", "danger")
        return None

@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    ticketform = TicketForm() 
    try:
        categories = db.session.scalars(db.select(event_category)).all()
        form.category.choices = [(category.id, category.name) for category in categories]
    except Exception as e:
        current_app.logger.error(f"Error loading categories for event creation: {e}")
        flash("Error loading page data. Please check category setup.", "danger")
        form.category.choices = []

    if request.method == 'POST':
        is_event_form_valid = form.validate_on_submit()
        is_ticketform_valid = ticketform.validate()

        if is_event_form_valid and is_ticketform_valid:
            image_filename_to_save = None
            if form.image.data and form.image.data.filename:
                image_filename_to_save = check_upload_file(form.image.data)
            
            new_event = Event(
                name=form.name.data,
                description=form.description.data,
                image_filename=image_filename_to_save,
                start_datetime=form.start_datetime.data,
                location=form.location.data,
                venue=form.venue.data,
                category_id=form.category.data,
                created_by=current_user.id,
                status='Open',
                genre=form.genre.data,
                age_limit=form.age_limit.data,
                length=form.length.data,
                artist_info=form.artist_info.data,
                policies=form.policies.data,
                facebook=form.facebook.data,
                instagram=form.instagram.data,
                twitter=form.twitter.data,
                youtube=form.youtube.data,
                twitch=form.twitch.data
            )
            try:
                db.session.add(new_event)
                db.session.flush()
                if ticketform.general_price.data is not None and ticketform.general_limit.data is not None:
                    general_ticket = ticket_type(
                        event_id=new_event.id, type_name='General Admission',
                        price=ticketform.general_price.data, quantity_available=ticketform.general_limit.data)
                    db.session.add(general_ticket)
                if ticketform.vip_price.data is not None and ticketform.vip_limit.data is not None:
                    vip_ticket = ticket_type(
                        event_id=new_event.id, type_name='VIP',
                        price=ticketform.vip_price.data, quantity_available=ticketform.vip_limit.data)
                    db.session.add(vip_ticket)
                if ticketform.balcony_price.data is not None and ticketform.balcony_limit.data is not None:
                    balcony_ticket = ticket_type(
                        event_id=new_event.id, type_name='Balcony',
                        price=ticketform.balcony_price.data, quantity_available=ticketform.balcony_limit.data)
                    db.session.add(balcony_ticket)
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
    event_to_edit = db.session.query(Event).filter_by(id=id).first_or_404()

    if event_to_edit.created_by != current_user.id:
        flash("You are not authorized to edit this event.", "danger")
        return redirect(url_for('event.details', id=id))

    form = EventForm(request.form if request.method == 'POST' else None, obj=event_to_edit)
    ticketform = TicketForm(request.form if request.method == 'POST' else None) 

    try:
        categories = db.session.scalars(db.select(event_category)).all()
        form.category.choices = [(category.id, category.name) for category in categories]
    except Exception as e:
        current_app.logger.error(f"Error loading categories for event editing: {e}")
        flash("Error loading page data. Please check category setup.", "danger")
        form.category.choices = []

    if request.method == 'POST':
        if form.validate() and ticketform.validate():
            form.populate_obj(event_to_edit) 

            if form.image.data and form.image.data.filename:
                new_image_filename = check_upload_file(form.image.data)
                if new_image_filename:
                    event_to_edit.image_filename = new_image_filename
            
            ticket_types_to_update = {
                'General Admission': (ticketform.general_price.data, ticketform.general_limit.data),
                'VIP': (ticketform.vip_price.data, ticketform.vip_limit.data),
                'Balcony': (ticketform.balcony_price.data, ticketform.balcony_limit.data)
            }

            for type_name_key, (price_data, limit_data) in ticket_types_to_update.items():
                existing_ticket = event_to_edit.ticket_types.filter_by(type_name=type_name_key).first()
                if price_data is not None and limit_data is not None:
                    if existing_ticket:
                        existing_ticket.price = float(price_data) 
                        existing_ticket.quantity_available = limit_data
                    else:
                        new_ticket = ticket_type(
                            event_id=event_to_edit.id,
                            type_name=type_name_key,
                            price=float(price_data), 
                            quantity_available=limit_data
                        )
                        db.session.add(new_ticket)
                elif existing_ticket:
                    db.session.delete(existing_ticket)
            try:
                db.session.commit()
                flash(f'Event "{event_to_edit.name}" updated successfully!', 'success')
                return redirect(url_for('event.details', id=event_to_edit.id))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating event: {e}")
                flash(f"Error updating event: {str(e)}", "danger")
    else: 
        form.category.data = event_to_edit.category_id 
        
        general_t = event_to_edit.ticket_types.filter_by(type_name='General Admission').first()
        if general_t:
            ticketform.general_price.data = int(general_t.price) if general_t.price is not None else None
            ticketform.general_limit.data = general_t.quantity_available
        
        vip_t = event_to_edit.ticket_types.filter_by(type_name='VIP').first()
        if vip_t:
            ticketform.vip_price.data = int(vip_t.price) if vip_t.price is not None else None
            ticketform.vip_limit.data = vip_t.quantity_available

        balcony_t = event_to_edit.ticket_types.filter_by(type_name='Balcony').first()
        if balcony_t:
            ticketform.balcony_price.data = int(balcony_t.price) if balcony_t.price is not None else None
            ticketform.balcony_limit.data = balcony_t.quantity_available

    return render_template('events/editEvent.html', form=form, ticketform=ticketform, event_id=event_to_edit.id, title=f"Edit Event: {event_to_edit.name}")

@eventbp.route('/<int:id>/cancel_confirm', methods=['GET'])
@login_required
def cancel_confirm(id):
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