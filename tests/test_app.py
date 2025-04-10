# Basic tests for app creation and core routes

def test_app_creation(test_app):
    """Test if the Flask app instance is created correctly."""
    assert test_app is not None
    assert test_app.config['TESTING'] is True
    assert 'sqlite:///:memory:' in test_app.config['SQLALCHEMY_DATABASE_URI']

def test_index_route_unauthenticated(test_client):
    """Test the index route '/' when not logged in."""
    response = test_client.get('/')
    assert response.status_code == 200 # Should serve index.html
    assert b"Welcome to ResumeGen AI" in response.data # Check for landing page content

# Add more tests here later for other routes, authentication, API endpoints etc.
# Example: Test login page loads
def test_login_page_loads(test_client):
    response = test_client.get('/auth/login')
    assert response.status_code == 200
    assert b"Login" in response.data

# Example: Test profile page requires login
def test_profile_page_redirects(test_client):
    response = test_client.get('/profile', follow_redirects=False) # Don't follow redirect yet
    assert response.status_code == 302 # Should redirect to login
    assert '/auth/login' in response.location # Check redirect location

    response = test_client.get('/profile', follow_redirects=True) # Follow redirect
    assert response.status_code == 200
    assert b"Login" in response.data # Should end up on login page
