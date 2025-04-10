import pytest
from flask import url_for, json, jsonify # Import jsonify
from unittest.mock import patch
# Import db and User for counter checks
from backend.app import db
from backend.models import User

# Helper function to log in
def login(client, username, password):
    return client.post(url_for('auth.login'), data={'username': username, 'password': password}, follow_redirects=True)

# --- Resume Generation Tests ---

@pytest.mark.parametrize("endpoint", ['generation_api.generate_resume', 'generation_api.extract_keywords', 'generation_api.generate_cover_letter'])
def test_generation_unauthenticated(test_client, test_app, endpoint):
    """Test generation endpoints require login."""
    with test_app.app_context():
        response = test_client.post(url_for(endpoint), json={})
    assert response.status_code == 302 # Redirects to login
    assert '/auth/login' in response.location

@patch('backend.generation_api.get_profile') # Mock get_profile
@patch('backend.generation_api.genai.GenerativeModel') # Mock Gemini Model
def test_generate_resume_success(mock_gemini_model, mock_get_profile, test_client, new_user, test_app):
    """Test successful resume generation."""
    # Setup mocks
    mock_get_profile.return_value = (jsonify({ # Simulate successful profile fetch
        'username': new_user.username,
        'personal_info': {'full_name': 'Test User'},
            # Add missing fields to mock experience data
            'experiences': [{'job_title': 'Tester', 'company_name': 'Mock Inc.', 'location': 'Testville'}],
            'educations': [], 'skills': [], 'projects': []
        }), 200)
    mock_model_instance = mock_gemini_model.return_value
    mock_model_instance.generate_content.return_value.text = "Generated Resume Text"

    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('generation_api.generate_resume'), json={'job_description': 'Test JD'})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'resume_text' in data
    assert data['resume_text'] == "Generated Resume Text"
    mock_model_instance.generate_content.assert_called_once() # Check API was called

    # Check counter incremented (optional but good)
    with test_app.app_context():
        user = db.session.get(User, new_user.id)
        assert user.resume_generations == 1

def test_generate_resume_no_jd(test_client, new_user, test_app):
    """Test resume generation without job description."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('generation_api.generate_resume'), json={}) # Missing job_description
    assert response.status_code == 400
    assert b"Job description is required" in response.data

@patch('backend.generation_api.get_profile') # Mock get_profile
def test_generate_resume_empty_profile(mock_get_profile, test_client, new_user, test_app):
    """Test resume generation with an empty profile."""
    mock_get_profile.return_value = (jsonify({ # Simulate empty profile
         'username': new_user.username,
         'personal_info': {}, 'experiences': [], 'educations': [], 'skills': [], 'projects': []
    }), 200)

    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('generation_api.generate_resume'), json={'job_description': 'Test JD'})
    assert response.status_code == 400
    assert b"Please complete your profile" in response.data

# --- Keyword Extraction Tests ---

def test_extract_keywords_success(test_client, new_user, test_app):
    """Test successful keyword extraction."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('generation_api.extract_keywords'), json={'job_description': 'Analyze this python and flask job.'})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'keywords' in data
    assert isinstance(data['keywords'], list)
    # Check for expected keywords (adjust based on NLTK processing)
    assert 'python' in data['keywords']
    assert 'flask' in data['keywords']
    assert 'job' in data['keywords']

def test_extract_keywords_no_jd(test_client, new_user, test_app):
    """Test keyword extraction without job description."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('generation_api.extract_keywords'), json={})
    assert response.status_code == 400
    assert b"Missing job description" in response.data

# --- Cover Letter Generation Tests ---

@patch('backend.generation_api.get_profile') # Mock get_profile
@patch('backend.generation_api.genai.GenerativeModel') # Mock Gemini Model
def test_generate_cover_letter_success(mock_gemini_model, mock_get_profile, test_client, new_user, test_app):
    """Test successful cover letter generation."""
    mock_get_profile.return_value = (jsonify({ # Simulate successful profile fetch
        'username': new_user.username,
        'personal_info': {'full_name': 'Test User'}, # Need at least name
        'experiences': [], 'educations': [], 'skills': [], 'projects': []
    }), 200)
    mock_model_instance = mock_gemini_model.return_value
    mock_model_instance.generate_content.return_value.text = "Generated Cover Letter Text"

    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('generation_api.generate_cover_letter'), json={
            'job_description': 'Test JD',
            'company_name': 'Test Company'
        })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cover_letter_text' in data
    assert data['cover_letter_text'] == "Generated Cover Letter Text"
    mock_model_instance.generate_content.assert_called_once()

    # Check counter incremented
    with test_app.app_context():
        user = db.session.get(User, new_user.id)
        assert user.cover_letter_generations == 1

def test_generate_cover_letter_missing_input(test_client, new_user, test_app):
    """Test cover letter generation with missing company or JD."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        # Missing company_name
        response1 = test_client.post(url_for('generation_api.generate_cover_letter'), json={'job_description': 'Test JD'})
        # Missing job_description
        response2 = test_client.post(url_for('generation_api.generate_cover_letter'), json={'company_name': 'Test Co'})

    assert response1.status_code == 400
    assert b"company name are required" in response1.data
    assert response2.status_code == 400
    assert b"Job description and company name are required" in response2.data

@patch('backend.generation_api.get_profile') # Mock get_profile
def test_generate_cover_letter_empty_profile(mock_get_profile, test_client, new_user, test_app):
    """Test cover letter generation with an empty profile (missing name)."""
    mock_get_profile.return_value = (jsonify({ # Simulate empty profile
         'username': new_user.username,
         'personal_info': {}, 'experiences': [], 'educations': [], 'skills': [], 'projects': []
    }), 200)

    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('generation_api.generate_cover_letter'), json={
            'job_description': 'Test JD',
            'company_name': 'Test Company'
        })
    assert response.status_code == 400
    assert b"Please complete your profile (at least name)" in response.data
