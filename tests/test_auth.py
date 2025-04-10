import pytest
from flask import url_for
# Assuming User model is in backend.models
from backend.models import User

def test_register_page_loads(test_client, test_app): # Add test_app fixture
    """Test that the registration page loads correctly."""
    with test_app.app_context(): # Wrap in app context
        response = test_client.get(url_for('auth.register'))
    assert response.status_code == 200
    assert b"Register" in response.data

def test_successful_registration(test_client, test_app):
    """Test successful user registration and redirection."""
    with test_app.app_context(): # Wrap in app context
        response = test_client.post(url_for('auth.register'), data={
            'username': 'newuser',
            'password': 'password'
    }, follow_redirects=False) # Don't follow redirect initially

    # Check for redirect to profile page
    assert response.status_code == 302
    # Check the redirect location points to the profile page
    assert response.location == '/profile' # Check relative path directly

    # Verify user was created in the database
    with test_app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.check_password('password')

def test_registration_existing_user(test_client, new_user, test_app): # Add test_app fixture
    """Test registration attempt with an existing username."""
    with test_app.app_context(): # Wrap in app context
        # Use follow_redirects=False to check the redirect itself
        response = test_client.post(url_for('auth.register'), data={
            'username': new_user.username, # Use the username from the fixture
            'password': 'newpassword'
        }, follow_redirects=False)

    # Should redirect back to register page on failure
    assert response.status_code == 302
    assert response.location == '/auth/register' # Check relative path directly
    # We cannot easily check flash messages without following redirects AND session handling
    # So we rely on the redirect target being correct for now.

# Remove duplicate test - test_app.py already covers this for unauthenticated
# def test_login_page_loads(test_client, test_app): ...

def test_successful_login(test_client, new_user, test_app): # Add test_app fixture
    """Test successful user login and redirection."""
    with test_app.app_context(): # Wrap in app context
        response = test_client.post(url_for('auth.login'), data={
            'username': new_user.username,
            'password': 'password' # Use the correct password from fixture
        }, follow_redirects=False)

    assert response.status_code == 302
    assert response.location == '/profile' # Check relative path directly

def test_login_invalid_username(test_client, test_app): # Add test_app fixture
    """Test login with a non-existent username."""
    with test_app.app_context(): # Wrap in app context
        response = test_client.post(url_for('auth.login'), data={
            'username': 'nonexistentuser',
            'password': 'password'
        }, follow_redirects=False) # Use follow_redirects=False

    # Should redirect back to login page on failure
    assert response.status_code == 302
    assert response.location == '/auth/login' # Check relative path directly
    # Cannot easily check flash message here

def test_login_invalid_password(test_client, new_user, test_app): # Add test_app fixture
    """Test login with an existing username but wrong password."""
    with test_app.app_context(): # Wrap in app context
        response = test_client.post(url_for('auth.login'), data={
            'username': new_user.username,
            'password': 'wrongpassword'
        }, follow_redirects=False) # Use follow_redirects=False

     # Should redirect back to login page on failure
    assert response.status_code == 302
    assert response.location == '/auth/login' # Check relative path directly
    # Cannot easily check flash message here

def test_logout(test_client, new_user, test_app): # Add test_app fixture
    """Test logging out."""
    # First, log in the user
    with test_app.app_context(): # Wrap login post
        test_client.post(url_for('auth.login'), data={
            'username': new_user.username,
            'password': 'password'
        })

    # Now, test the logout route
    with test_app.app_context(): # Wrap logout get
        response = test_client.get(url_for('auth.logout'), follow_redirects=False)
    assert response.status_code == 302
    assert response.location == '/auth/login' # Check relative path directly

    # Verify user is logged out by trying to access profile page
    response = test_client.get(url_for('pages.profile'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data # Should end up on login page
