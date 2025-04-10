import pytest
from flask import url_for, json
# Assuming User model is in backend.models
from backend.models import User, PersonalInfo, Experience, Education, Skill, Project

# Helper function to log in a user via test client
def login(client, username, password):
    return client.post(url_for('auth.login'), data={'username': username, 'password': password}, follow_redirects=True)

def test_get_profile_unauthenticated(test_client, test_app):
    """Test accessing get_profile without logging in."""
    with test_app.app_context():
        response = test_client.get(url_for('profile_api.get_profile'))
    # Should redirect to login (or return 401 if API) - Flask-Login redirects by default
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_get_profile_authenticated_empty(test_client, new_user, test_app):
    """Test getting an empty profile after logging in."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.get(url_for('profile_api.get_profile'))

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == new_user.username
    assert data['personal_info'] == {} # Should be empty initially
    assert data['experiences'] == []
    assert data['educations'] == []
    assert data['skills'] == []
    assert data['projects'] == []

def test_save_profile_unauthenticated(test_client, test_app):
    """Test saving profile without logging in."""
    profile_data = {'personal_info': {'full_name': 'Test Name'}}
    with test_app.app_context():
        response = test_client.post(url_for('profile_api.save_profile'), json=profile_data)
    assert response.status_code == 302 # Redirects to login
    assert '/auth/login' in response.location

def test_save_and_get_profile(test_client, new_user, test_app):
    """Test saving profile data and then retrieving it."""
    profile_data_to_save = {
        'personal_info': {
            'full_name': 'Test User',
            'email_address': 'test@example.com',
            'phone_number': '123-456-7890',
            'location': 'Test City, TS',
            'linkedin_url': 'https://linkedin.com/in/testuser',
            'portfolio_url': 'https://testuser.com',
            'target_job': 'Tester'
        },
        'experiences': [
            {'job_title': 'Test Job 1', 'company_name': 'Test Co', 'location': 'Remote', 'start_date': 'Jan 2022', 'end_date': 'Present', 'description': 'Did testing.'}
        ],
        'educations': [
            {'degree_name': 'B.S. Testing', 'major': 'Testing', 'institution_name': 'Test University', 'location': 'Testville, TS', 'graduation_date': 'May 2021'}
        ],
        'skills': [
            {'skill_name': 'Pytest'},
            {'skill_name': 'Flask'}
        ],
        'projects': [
            {'project_name': 'Test Project', 'description': 'A project for testing.', 'link': 'https://github.com/test/test'}
        ]
    }

    with test_app.app_context():
        # Log in
        login(test_client, new_user.username, 'password')

        # Save profile
        save_response = test_client.post(url_for('profile_api.save_profile'), json=profile_data_to_save)
        assert save_response.status_code == 200
        assert 'Profile saved successfully' in save_response.get_json()['message']

        # Get profile
        get_response = test_client.get(url_for('profile_api.get_profile'))
        assert get_response.status_code == 200
        retrieved_data = get_response.get_json()

    # Assertions (ignoring IDs as they are auto-generated)
    assert retrieved_data['username'] == new_user.username
    assert retrieved_data['personal_info']['full_name'] == 'Test User'
    assert retrieved_data['personal_info']['email_address'] == 'test@example.com'
    # ... add more assertions for other personal info fields ...

    assert len(retrieved_data['experiences']) == 1
    assert retrieved_data['experiences'][0]['job_title'] == 'Test Job 1'
    assert retrieved_data['experiences'][0]['description'] == 'Did testing.'
    # ... add more assertions for other experience fields ...

    assert len(retrieved_data['educations']) == 1
    assert retrieved_data['educations'][0]['degree_name'] == 'B.S. Testing'
    # ... add more assertions for other education fields ...

    assert len(retrieved_data['skills']) == 2
    skill_names = {s['skill_name'] for s in retrieved_data['skills']}
    assert 'Pytest' in skill_names
    assert 'Flask' in skill_names

    assert len(retrieved_data['projects']) == 1
    assert retrieved_data['projects'][0]['project_name'] == 'Test Project'
    # ... add more assertions for other project fields ...

def test_save_empty_profile(test_client, new_user, test_app):
    """Test saving an empty profile payload."""
    empty_profile_data = {
        'personal_info': {},
        'experiences': [],
        'educations': [],
        'skills': [],
        'projects': []
    }
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        save_response = test_client.post(url_for('profile_api.save_profile'), json=empty_profile_data)
        assert save_response.status_code == 200

        # Verify data is empty or default
        get_response = test_client.get(url_for('profile_api.get_profile'))
        assert get_response.status_code == 200
        retrieved_data = get_response.get_json()

        assert retrieved_data['personal_info']['full_name'] == None # Or '' depending on model default
        assert retrieved_data['experiences'] == []
        assert retrieved_data['educations'] == []
        assert retrieved_data['skills'] == []
        assert retrieved_data['projects'] == []
