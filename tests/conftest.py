import pytest
import os
import tempfile
import nltk # Import nltk

# Adjust the import path based on your project structure
# This assumes tests/ is at the same level as backend/
from backend.app import create_app, db
from backend.config import Config

class TestConfig(Config):
    """Configuration for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    SERVER_NAME = 'localhost.test' # Add a dummy server name for url_for

@pytest.fixture(scope='module')
def test_app():
    """Create and configure a new app instance for each test module."""
    # Create a temporary instance folder path
    instance_path = tempfile.mkdtemp()
    TestConfig.instance_path = instance_path # Override instance path for tests

    app = create_app(TestConfig)

    # Establish an application context
    with app.app_context():
        # Create the database tables
        db.create_all()

    yield app # Provide the app instance to the tests

    # Clean up / close the database and remove temp instance folder
    with app.app_context():
        db.session.remove()
        # db.drop_all() # Optional: drop tables if needed
    # Clean up temp instance folder
    # Note: This might require shutil.rmtree if not empty
    try:
        os.rmdir(instance_path)
    except OSError:
        pass # Ignore if cleanup fails

@pytest.fixture(scope='function') # Change scope to function
def test_client(test_app):
    """A test client for the app, created fresh for each test function."""
    return test_app.test_client()

@pytest.fixture(scope='module')
def runner(test_app):
    """A test runner for the app's Click commands."""
    return test_app.test_cli_runner()

# You can add more fixtures here, e.g., for creating test users
@pytest.fixture(scope='function') # Function scope to get clean user per test
def new_user(test_app):
    """Fixture to create a new user for testing."""
    from backend.models import User # Keep import local to fixture
    with test_app.app_context():
        user = User(username='testuser')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        yield user
        # Clean up user after test
        db.session.delete(user)
        db.session.commit()

@pytest.fixture(scope='session', autouse=True)
def download_nltk_data():
    """Ensure necessary NLTK data is downloaded once per session."""
    required_data = ['punkt', 'stopwords', 'wordnet', 'punkt_tab']
    for data_item in required_data:
        try:
            nltk.data.find(f'tokenizers/{data_item}' if data_item.startswith('punkt') else f'corpora/{data_item}')
            print(f"NLTK data '{data_item}' found.")
        except LookupError:
            print(f"Downloading NLTK '{data_item}' data...")
            try:
                nltk.download(data_item, quiet=True)
            except Exception as e:
                print(f"Warning: Failed to download NLTK data '{data_item}': {e}")
                # Depending on strictness, you might want to raise an error here
                # if certain data is absolutely essential for tests to run.
                pass
