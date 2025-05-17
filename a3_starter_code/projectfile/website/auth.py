from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

# this is a hint for a login function
@auth_bp.route('/login', methods=['GET', 'POST'])
# view function
def login():
    login_form = LoginForm()
    error = None
    if(login_form.validate_on_submit()==True):
        #get the username and password from the database
        email = login_form.email.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.email==email))
        #if there is no user with that name
        if user is None:
            error = 'Incorrect username'#could be a security risk to give this much info away
        #check the password - notice password hash function
        elif not check_password_hash(user.password_hash, password): # takes the hash and password
            error = 'Incorrect password'
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash(error)
    return render_template('user.html', form=login_form, heading='Login')





@auth_bp.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if (form.validate_on_submit()==True):
        firstName = form.firstName.data
        surname = form.surname.data
        phoneNumber= form.mobileNumber.data
        address = form.streetAddress.data
        pwd = form.password.data
        email = form.email.data

        #check if a user exists
        user = db.session.scalar(db.select(User).where(User.email==email))

        if user:#this returns true when user is not None
            flash('Email already registered, please try another')
            return redirect(url_for('auth.register'))
        
        # don't store the password in plaintext!
        pwd_hash = generate_password_hash(pwd)
        #create a new User model object
        new_user = User(firstName=firstName,surname=surname,mobileNumber=phoneNumber, streetAddress=address, password_hash=pwd_hash, email=email)
        db.session.add(new_user)
        db.session.commit()

        print('Successfully registered')
        flash('You successfully registered your account')
        #commit to the database and redirect to HTML page
        return redirect(url_for('main.index'))


        #return redirect(url_for('auth.login'))
    
        #the else is called when the HTTP request calling this page is a GET
    else:
        return render_template('user.html', form=form, heading='Register')
    #return render_template('user.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
