from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from .models import Event, Comment, ticket_type
from .forms import EventForm
from .forms import TicketForm
from .forms import CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

eventbp = Blueprint('event', __name__, url_prefix='/events')

@eventbp.route('/<id>')
def details(id):
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))
    
    cform = CommentForm()
    return render_template('events/eventDetails.html', event=event, form=cform)

@eventbp.route('/create', methods = ['GET', 'POST'])
def create():
  print('Method type: ', request.method)
  form = EventForm()
  ticketform = TicketForm()
  if form.validate_on_submit() and ticketform.validate_on_submit():
    db_file_path = check_upload_file(form)
    event = Event(
      name=form.name.data,
      description=form.description.data, 
      image_url = db_file_path,
      genre=form.genre.data,
      age_limit=form.age_limit.data,
      start_date=form.start_date.data,
      end_date=form.end_date.data,
      end_time=form.end_time.data,
      length=form.length.data,
      venue=form.venue.data,
      location=form.location.data,
      artist_info=form.artist_info.data,
      policies=form.policies.data,
      facebook=form.facebook.data,
      instagram= form.instagram.data,
      twitter= form.twitter.data,
      twitch = form.twitch.data,
    )
  
    # add the object to the db session
    db.session.add(event)
    # commit to the database
    db.session.commit()



    # Add ticket types if provided
    if ticketform.general_price.data and ticketform.general_limit.data:
        general = ticket_type(
            event_id=event.id,
            type_name='General',
            description='General Admission',
            price=ticketform.general_price.data,
            quantity=ticketform.general_limit.data
        )
        db.session.add(general)

    if ticketform.vip_price.data and ticketform.vip_limit.data:
        vip = ticket_type(
            event_id=event.id,
            type_name='VIP',
            description='VIP Access',
            price=ticketform.vip_price.data,
            quantity=ticketform.vip_limit.data
        )
        db.session.add(vip)

    if ticketform.balcony_price.data and ticketform.balcony_limit.data:
        balcony = ticket_type(
            event_id=event.id,
            type_name='Balcony',
            description='Balcony Seating',
            price=ticketform.balcony_price.data,
            quantity=ticketform.balcony_limit.data
        )
        db.session.add(balcony)
    
    db.session.commit()

    print('Successfully created new event')
    #Always end with redirect when form is valid
    return redirect(url_for('event.create'))
  return render_template('events/eventCreation.html', form=form, ticketform=ticketform)

def check_upload_file(form):
  # get file data from form  
  fp = form.image.data
  filename = fp.filename
  # get the current path of the module file… store image file relative to this path  
  BASE_PATH = os.path.dirname(__file__)
  # upload file location – directory of this file/static/image
  upload_path = os.path.join(BASE_PATH,'static/image',secure_filename(filename))
  # store relative path in DB as image location in HTML is relative
  db_upload_path = '/static/image/' + secure_filename(filename)
  # save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path

@eventbp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm()
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))
    
    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            event=event,
            user=current_user
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added', 'success')
    
    return redirect(url_for('event.details', id=id))