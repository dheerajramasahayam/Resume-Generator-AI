import pytest
from flask import url_for, json
from backend.models import User, db

# Helper function to log in
def login(client, username, password):
    return client.post(url_for('auth.login'), data={'username': username, 'password': password}, follow_redirects=True)

# Fixture to create an admin user
@pytest.fixture(scope='function')
def admin_user(test_app):
    with test_app.app_context():
        admin = User(username='adminuser', is_admin=True)
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        yield admin
        # Clean up admin user
        db.session.delete(admin)
        db.session.commit()

# Fixture for a regular user (can reuse new_user from conftest)
# from tests.conftest import new_user

# --- Test Access Control ---

@pytest.mark.parametrize("route_name", ['admin.dashboard', 'admin.list_users'])
def test_admin_routes_unauthenticated(test_client, test_app, route_name):
    """Test admin routes redirect unauthenticated users."""
    with test_app.app_context():
        response = test_client.get(url_for(route_name))
    assert response.status_code == 302
    assert '/auth/login' in response.location

@pytest.mark.parametrize("route_name", ['admin.dashboard', 'admin.list_users'])
def test_admin_routes_non_admin(test_client, new_user, test_app, route_name):
    """Test admin routes return 403 for non-admin users."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.get(url_for(route_name))
    assert response.status_code == 403 # Forbidden

# --- Test Admin Functionality ---

def test_admin_dashboard_loads(test_client, admin_user, test_app):
    """Test admin dashboard loads for admin user."""
    with test_app.app_context():
        login(test_client, admin_user.username, 'password')
        response = test_client.get(url_for('admin.dashboard'))
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data
    assert bytes(f"Welcome, {admin_user.username}!", 'utf-8') in response.data
    assert b"Total Registered Users:" in response.data

def test_admin_user_list_loads(test_client, admin_user, new_user, test_app):
    """Test user list page loads and shows users."""
    with test_app.app_context():
        login(test_client, admin_user.username, 'password')
        response = test_client.get(url_for('admin.list_users'))
    assert response.status_code == 200
    assert b"Manage Users" in response.data
    assert bytes(admin_user.username, 'utf-8') in response.data # Admin should be listed
    assert bytes(new_user.username, 'utf-8') in response.data # Regular user should be listed
    assert b"Make Admin" in response.data # Button for regular user
    assert b"Remove Admin" in response.data # Button for admin user (likely disabled)

def test_admin_toggle_admin_status(test_client, admin_user, new_user, test_app):
    """Test toggling admin status for a regular user."""
    with test_app.app_context():
        login(test_client, admin_user.username, 'password')
        # Check initial status
        user_before = db.session.get(User, new_user.id)
        assert user_before.is_admin is False

        # Toggle to admin
        response_make_admin = test_client.post(url_for('admin.toggle_admin', user_id=new_user.id), follow_redirects=True)
        assert response_make_admin.status_code == 200 # Should redirect back to list successfully
        # Cannot reliably check flash message content here after redirect
        user_after_make = db.session.get(User, new_user.id)
        assert user_after_make.is_admin is True

        # Toggle back to non-admin
        response_remove_admin = test_client.post(url_for('admin.toggle_admin', user_id=new_user.id), follow_redirects=True)
        assert response_remove_admin.status_code == 200 # Should redirect back to list successfully
        # Cannot reliably check flash message content here after redirect
        user_after_remove = db.session.get(User, new_user.id)
        assert user_after_remove.is_admin is False

def test_admin_cannot_toggle_self(test_client, admin_user, test_app):
    """Test admin cannot toggle their own admin status."""
    with test_app.app_context():
        login(test_client, admin_user.username, 'password')
        response = test_client.post(url_for('admin.toggle_admin', user_id=admin_user.id), follow_redirects=True)
    assert response.status_code == 200
    assert b"You cannot remove your own admin privileges." in response.data
    # Verify status didn't change
    with test_app.app_context():
        user = db.session.get(User, admin_user.id)
        assert user.is_admin is True

def test_admin_delete_user(test_client, admin_user, new_user, test_app):
    """Test deleting a regular user."""
    with test_app.app_context():
        login(test_client, admin_user.username, 'password')
        user_id_to_delete = new_user.id
        username_to_delete = new_user.username

        # Ensure user exists before delete
        assert db.session.get(User, user_id_to_delete) is not None

        # Delete user
        response = test_client.post(url_for('admin.delete_user', user_id=user_id_to_delete), follow_redirects=True)
        assert response.status_code == 200 # Should redirect back to list successfully
        # Cannot reliably check flash message content here after redirect

        # Ensure user is gone
        assert db.session.get(User, user_id_to_delete) is None

def test_admin_cannot_delete_self(test_client, admin_user, test_app):
    """Test admin cannot delete their own account."""
    with test_app.app_context():
        login(test_client, admin_user.username, 'password')
        response = test_client.post(url_for('admin.delete_user', user_id=admin_user.id), follow_redirects=True)
    assert response.status_code == 200
    assert b"You cannot delete your own account from here." in response.data
    # Verify admin still exists
    with test_app.app_context():
        assert db.session.get(User, admin_user.id) is not None

def test_admin_view_user_loads(test_client, admin_user, new_user, test_app):
    """Test the user detail view loads correctly for an admin."""
    with test_app.app_context():
        login(test_client, admin_user.username, 'password')
        response = test_client.get(url_for('admin.view_user', user_id=new_user.id))

    assert response.status_code == 200
    # Check if it returns JSON as currently implemented
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert 'user' in data
    assert 'profile' in data
    assert data['user']['id'] == new_user.id
    assert data['user']['username'] == new_user.username

# Note: Further tests for view_user template rendering would require updating
# the route to use render_template and creating admin_user_detail.html.
