import pytest
from flask import url_for, json
import io

# Helper function to log in
def login(client, username, password):
    # Need app context for url_for inside helper
    return client.post(url_for('auth.login'), data={'username': username, 'password': password}, follow_redirects=True)

@pytest.mark.parametrize("export_format", ['docx', 'pdf'])
def test_export_unauthenticated(test_client, test_app, export_format):
    """Test export endpoint requires login."""
    with test_app.app_context():
        response = test_client.post(url_for('export_api.export_resume'), json={
            'resume_text': 'Some text',
            'format': export_format,
            'template': 'simple'
        })
    assert response.status_code == 302
    assert '/auth/login' in response.location

@pytest.mark.parametrize("template", ['simple', 'classic', 'modern'])
def test_export_docx_success(test_client, new_user, test_app, template):
    """Test successful DOCX export for different templates."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('export_api.export_resume'), json={
            'resume_text': '### Section\n* Bullet 1\n**Bold Title**\nRegular text.',
            'format': 'docx',
            'template': template
        })

    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert 'attachment; filename=resume.docx' in response.headers['Content-Disposition']
    # Check if the response data looks like a DOCX file (starts with PK zip header)
    assert response.data.startswith(b'PK\x03\x04')

@pytest.mark.parametrize("template", ['simple', 'classic', 'modern'])
def test_export_pdf_success(test_client, new_user, test_app, template):
    """Test successful PDF export for different templates."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('export_api.export_resume'), json={
            'resume_text': '### Section\n* Bullet 1\n**Bold Title**\nRegular text.',
            'format': 'pdf',
            'template': template
        })

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    assert 'attachment; filename=resume.pdf' in response.headers['Content-Disposition']
    # Check if the response data looks like a PDF file (starts with %PDF)
    assert response.data.startswith(b'%PDF-')

def test_export_missing_data(test_client, new_user, test_app):
    """Test export with missing resume_text or format."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        # Missing text
        response1 = test_client.post(url_for('export_api.export_resume'), json={'format': 'docx', 'template': 'simple'})
        # Missing format
        response2 = test_client.post(url_for('export_api.export_resume'), json={'resume_text': 'abc', 'template': 'simple'})

    assert response1.status_code == 400
    assert b"Missing resume text or format" in response1.data
    assert response2.status_code == 400
    assert b"Missing resume text or format" in response2.data

def test_export_invalid_format(test_client, new_user, test_app):
    """Test export with an invalid format."""
    with test_app.app_context():
        login(test_client, new_user.username, 'password')
        response = test_client.post(url_for('export_api.export_resume'), json={
            'resume_text': 'Some text',
            'format': 'txt', # Invalid format
            'template': 'simple'
        })
    assert response.status_code == 400
    assert b"Invalid export format" in response.data
