from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from .forms import LoginForm, RegisterForm, UpdateProfileForm
from . import db

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

# view function for login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = db.session.scalar(
            db.select(User).where(User.emailid == email)
        )
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(next_page)
        flash('Invalid email or password', 'danger')
    return render_template('user.html', form=login_form, heading='Login')

# view function for registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        hashed_pw = generate_password_hash(register_form.password.data)
        new_user = User(
            name=f"{register_form.first_name.data} {register_form.surname.data}",
            emailid=register_form.email.data,
            password_hash=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created, please log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('user.html', form=register_form, heading='Register')

# view function for logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# view function for profile update
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    # Pre-populate on GET
    if request.method == 'GET':
        form.email.data   = current_user.emailid
        form.phone.data   = current_user.phone or ''
        form.address.data = current_user.address or ''

    if form.validate_on_submit():
        # Update contact details
        current_user.phone   = form.phone.data
        current_user.address = form.address.data

        # Handle password change if requested
        if form.new_password.data:
            if not check_password_hash(current_user.password_hash, form.current_password.data):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.password_hash = generate_password_hash(form.new_password.data)

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('user.html', form=form, heading='Update Profile')