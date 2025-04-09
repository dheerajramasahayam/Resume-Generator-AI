from flask import Blueprint, redirect, url_for, current_app, render_template # Add render_template
from flask_login import login_required, current_user
import os # Needed for template path

# Using 'pages' as the blueprint name to avoid conflict if 'main' is used elsewhere
# Define template folder relative to this blueprint file's location
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
template_folder = frontend_dir
# Register blueprint only with template folder (static is handled by app)
pages = Blueprint('pages', __name__, template_folder=template_folder)


@pages.route('/')
def index():
    # Serve the landing page if user is not logged in
    if current_user.is_authenticated:
        return redirect(url_for('pages.profile')) # Point to the profile route in this blueprint
    # Render the index.html template
    return render_template('index.html')

@pages.route('/profile')
@login_required
def profile():
    # Render the profile template, passing the user
    return render_template('profile.html', current_user=current_user)

@pages.route('/generate_page')
@login_required
def generate_page():
     # Render the generate template, passing the user
    return render_template('generate.html', current_user=current_user)

@pages.route('/resume_display')
@login_required
def resume_display():
     # Render the resume display template, passing the user
    return render_template('resume.html', current_user=current_user)

@pages.route('/cover_letter')
@login_required
def cover_letter():
     # Render the cover letter template, passing the user
    return render_template('cover_letter.html', current_user=current_user)
