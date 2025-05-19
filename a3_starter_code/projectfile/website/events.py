from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from .models import Event, Comment, ticket_type, event_category
from .forms import EventForm, TicketForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

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
        print("--- POST Request Received ---")
        print(f"Request form data for general_limit: {request.form.get('general_limit')}")
        
        is_event_form_valid = form.validate_on_submit()
        print(f"EventForm valid (validate_on_submit): {is_event_form_valid}")
        if not is_event_form_valid:
            print(f"EventForm errors: {form.errors}")

        is_ticketform_valid = ticketform.validate()
        print(f"TicketForm general_limit data: {ticketform.general_limit.data}")
        print(f"TicketForm general_limit errors: {ticketform.general_limit.errors}")
        print(f"TicketForm valid (validate): {is_ticketform_valid}")
        if not is_ticketform_valid:
            print(f"TicketForm errors: {ticketform.errors}")

        if is_event_form_valid and is_ticketform_valid:
            print("--- Both forms appear valid, proceeding to create event ---")
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
                    print(f"Creating general ticket with limit: {ticketform.general_limit.data}")
                    general_ticket = ticket_type(
                        event_id=new_event.id,
                        type_name='General Admission',
                        price=ticketform.general_price.data,
                        quantity_available=ticketform.general_limit.data
                    )
                    db.session.add(general_ticket)

                if ticketform.vip_price.data is not None and ticketform.vip_limit.data is not None:
                    print(f"Creating VIP ticket with limit: {ticketform.vip_limit.data}")
                    vip_ticket = ticket_type(
                        event_id=new_event.id,
                        type_name='VIP',
                        price=ticketform.vip_price.data,
                        quantity_available=ticketform.vip_limit.data
                    )
                    db.session.add(vip_ticket)

                if ticketform.balcony_price.data is not None and ticketform.balcony_limit.data is not None:
                    print(f"Creating Balcony ticket with limit: {ticketform.balcony_limit.data}")
                    balcony_ticket = ticket_type(
                        event_id=new_event.id,
                        type_name='Balcony',
                        price=ticketform.balcony_price.data,
                        quantity_available=ticketform.balcony_limit.data
                    )
                    db.session.add(balcony_ticket)
                
                db.session.commit()
                flash(f'Event "{new_event.name}" created successfully!', 'success')
                return redirect(url_for('event.details', id=new_event.id))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating event: {e}")
                flash(f"Error creating event: {str(e)}", "danger")
        else:
            print("--- Form validation failed, re-rendering template ---")

    return render_template('events/eventCreation.html', form=form, ticketform=ticketform, title="Create New Event")

@eventbp.route('/<int:id>/comment', methods=['POST'])
@login_required
def comment(id):
    form = CommentForm()
    event = db.session.query(Event).filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        new_comment = Comment(
            text=form.text.data,
            event_id=event.id,
            user_id=current_user.id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been added successfully.', 'success')
    else:
        for field, errors_list in form.errors.items():
            for error in errors_list:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('event.details', id=id))