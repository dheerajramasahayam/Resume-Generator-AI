import os
# Add render_template, remove send_from_directory if no longer needed elsewhere
from flask import Blueprint, redirect, url_for, request, flash, current_app, render_template
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, PersonalInfo
from .app import db

# Define template folder relative to this blueprint file's location
template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
auth = Blueprint('auth', __name__, template_folder=template_folder)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pages.profile')) # Corrected blueprint name

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.')
            # Redirect back to the login page
            return redirect(url_for('auth.login'))

        # If the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        # Redirect to the profile page after successful login
        return redirect(url_for('pages.profile')) # Corrected blueprint name

    # If GET request, render the login template
    # The template folder should be configured correctly for this blueprint or the app
    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pages.profile')) # Corrected blueprint name

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Add password confirmation if desired in the template
        # password_confirm = request.form.get('password_confirm')
        # if password != password_confirm:
        #     flash('Passwords do not match.')
        #     return redirect(url_for('auth.register'))

        user = User.query.filter_by(username=username).first() # Check if username already exists

        if user: # If a user is found, redirect back to registration page
            flash('Username already exists.')
            return redirect(url_for('auth.register'))

        # Create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(username=username)
        new_user.set_password(password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Create an empty PersonalInfo record for the new user
        new_personal_info = PersonalInfo(user_id=new_user.id)
        db.session.add(new_personal_info)
        db.session.commit()


        # Log in the new user
        login_user(new_user)

        flash('Registration successful! Please complete your profile.')
        # Redirect to the profile page after successful registration
        return redirect(url_for('pages.profile')) # Corrected blueprint name

    # If GET request, render the register template
    return render_template('register.html')


@auth.route('/logout')
@login_required # Ensure only logged-in users can logout
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login')) # Redirect to login page after logout
