from functools import wraps
from flask import Blueprint, render_template, abort, current_app, jsonify
from flask_login import login_required, current_user
import os # Import os
from functools import wraps
from flask import Blueprint, render_template, abort, current_app, jsonify
from flask_login import login_required, current_user
from flask import Blueprint, render_template, abort, current_app, jsonify, request, flash, redirect, url_for # Added request, flash, redirect, url_for
from flask_login import login_required, current_user
import os # Import os
from functools import wraps
from flask import Blueprint, render_template, abort, current_app, jsonify
from flask_login import login_required, current_user
# Import models needed for admin views
from .models import User, db # Import db

# Define template folder relative to this blueprint file's location
template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'admin'))
admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder=template_folder)


# --- Admin Required Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            # Abort with 403 Forbidden if not admin
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- Admin Routes ---
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get user count
    user_count = User.query.count()
    # Render the admin dashboard template, passing count
    return render_template('admin_dashboard.html', current_user=current_user, user_count=user_count)


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    try:
        users = User.query.order_by(User.id).all()
        # Render the user list template, passing the users
        return render_template('admin_users.html', users=users, current_user=current_user)
    except Exception as e:
        current_app.logger.error(f"Error fetching users for admin: {e}")
        return "Error fetching users.", 500

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        # Fetch profile data similarly to profile_api.get_profile
        personal_info = user.personal_info
        experiences = user.experiences.order_by(Experience.id).all()
        educations = user.educations.order_by(Education.id).all()
        skills = user.skills.order_by(Skill.id).all()
        projects = user.projects.order_by(Project.id).all()

        profile_data = {
            'personal_info': {
                'full_name': personal_info.full_name if personal_info else '',
                'phone_number': personal_info.phone_number if personal_info else '',
                'email_address': personal_info.email_address if personal_info else '',
                'linkedin_url': personal_info.linkedin_url if personal_info else '',
                'portfolio_url': personal_info.portfolio_url if personal_info else '',
                'location': personal_info.location if personal_info else '',
                'target_job': personal_info.target_job if personal_info else '',
            } if personal_info else {},
            'experiences': [{'id': exp.id, 'job_title': exp.job_title, 'company_name': exp.company_name, 'location': exp.location, 'start_date': exp.start_date, 'end_date': exp.end_date, 'description': exp.description} for exp in experiences],
            'educations': [{'id': edu.id, 'degree_name': edu.degree_name, 'major': edu.major, 'institution_name': edu.institution_name, 'location': edu.location, 'graduation_date': edu.graduation_date} for edu in educations],
            'skills': [{'id': skill.id, 'skill_name': skill.skill_name} for skill in skills],
            'projects': [{'id': proj.id, 'project_name': proj.project_name, 'description': proj.description, 'link': proj.link} for proj in projects],
        }
        # Render the detail template
        return render_template('admin_user_detail.html', user=user, profile_data=profile_data, current_user=current_user)

    except Exception as e:
        current_app.logger.error(f"Error fetching user {user_id} for admin: {e}")
        return "Error fetching user details.", 500

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    # Prevent admin from de-admining themselves
    if user_id == current_user.id:
        flash('You cannot remove your own admin privileges.', 'warning')
        return redirect(url_for('admin.list_users'))

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    try:
        db.session.add(user)
        db.session.commit()
        flash(f"Admin status for user '{user.username}' updated.", 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling admin for user {user_id}: {e}")
        flash('Error updating admin status.', 'danger')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
     # Prevent admin from deleting themselves
    if user_id == current_user.id:
        flash('You cannot delete your own account from here.', 'warning')
        return redirect(url_for('admin.list_users'))

    user = User.query.get_or_404(user_id)
    username_deleted = user.username # Store username for flash message
    try:
        # Cascade delete should handle related profile data
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{username_deleted}' has been deleted.", 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user {user_id}: {e}")
        flash('Error deleting user.', 'danger')
    return redirect(url_for('admin.list_users'))
