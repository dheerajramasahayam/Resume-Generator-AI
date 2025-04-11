import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Find the absolute path of the directory containing this file
basedir = os.path.abspath(os.path.dirname(__file__))
# Define the path for the instance folder (where the DB will live)
instance_path = os.path.join(os.path.dirname(basedir), 'backend', 'instance')
# MIGRATION_DIR definition removed from top level

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this'
    # Define the SQLAlchemy database URI. Use SQLite in the instance folder.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_path, 'resume_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    # Point MIGRATION_DIR to the 'db' directory in the project root
    MIGRATION_DIR = os.path.join(os.path.dirname(basedir), 'db')


    # Ensure the instance folder exists
    @staticmethod
    def init_app(app):
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        app.instance_path = instance_path
