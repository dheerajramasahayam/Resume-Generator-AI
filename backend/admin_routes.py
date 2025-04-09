from functools import wraps
from flask import Blueprint, render_template, abort, current_app, jsonify
from flask_login import login_required, current_user
# Import models needed for admin views
from .models import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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
    # For now, just serve a simple template
    # We'll create frontend/admin/admin_dashboard.html later
    # return render_template('admin/admin_dashboard.html')
    # Temporarily return simple message
    return "<h1>Admin Dashboard</h1><p>Welcome, Admin!</p><a href='/admin/users'>View Users</a> | <a href='/'>Main Site</a>"

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    try:
        users = User.query.order_by(User.id).all()
        # We'll create frontend/admin/admin_users.html later to display this nicely
        # return render_template('admin/admin_users.html', users=users)
        # Temporarily return JSON
        user_list = [{'id': u.id, 'username': u.username, 'is_admin': u.is_admin} for u in users]
        return jsonify(user_list)
    except Exception as e:
        current_app.logger.error(f"Error fetching users for admin: {e}")
        return "Error fetching users.", 500

# Add more admin routes here later (e.g., view user details, edit, delete)
