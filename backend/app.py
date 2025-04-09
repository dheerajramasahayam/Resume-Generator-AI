from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# Only import Config and instance_path directly
from .config import Config, instance_path
import os
import nltk # Import nltk
import click # Import click for CLI commands

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Redirect to login page if user is not authenticated
migrate = Migrate()

def create_app(config_class=Config):
    """Application factory function."""
    # Define path to the *static* folder within frontend
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))

    # Configure the main app's static folder
    app = Flask(__name__,
                instance_path=instance_path,
                instance_relative_config=True,
                static_folder=static_dir,      # Point to frontend/static
                static_url_path='/static')     # Serve files under /static URL

    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    login_manager.init_app(app)
    # Pass the configured migration directory to Flask-Migrate
    migrate.init_app(app, db, directory=app.config['MIGRATION_DIR'])

    # Ensure the instance folder exists (moved here from Config for clarity)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    # Register blueprints here
    from .auth_routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Register new blueprints
    from .page_routes import pages as pages_blueprint
    app.register_blueprint(pages_blueprint)

    from .profile_api import profile_api as profile_api_blueprint
    app.register_blueprint(profile_api_blueprint) # Prefix is defined in the blueprint

    from .generation_api import generation_api as generation_api_blueprint
    app.register_blueprint(generation_api_blueprint) # Prefix is defined in the blueprint

    from .export_api import export_api as export_api_blueprint
    app.register_blueprint(export_api_blueprint) # Prefix is defined in the blueprint

    from .admin_routes import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint) # Prefix is defined in the blueprint

    # Define the user loader function for Flask-Login
    from .models import User # Import the User model now that it exists
    @login_manager.user_loader
    def load_user(user_id):
        # Since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # Download NLTK data if not present (useful for deployment)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK 'punkt' data...")
        nltk.download('punkt', quiet=True)
        # Also download punkt_tab which might be needed by word_tokenize implicitly
        print("Downloading NLTK 'punkt_tab' data...")
        nltk.download('punkt_tab', quiet=True)
    except LookupError:
        # If punkt_tab download fails, maybe it's included with punkt? Log a warning.
        print("Warning: Could not download 'punkt_tab'. Proceeding...")
        pass # Allow app to continue if punkt_tab isn't strictly required or downloadable

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK 'stopwords' data...")
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK 'wordnet' data...")
        nltk.download('wordnet', quiet=True)

    # --- CLI Commands ---
    @app.cli.command("make-admin")
    @click.argument("username")
    def make_admin(username):
        """Assign admin privileges to a user."""
        from .models import User # Import here to avoid circular dependency issues
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_admin = True
            db.session.add(user)
            db.session.commit()
            print(f"User '{username}' is now an admin.")
        else:
            print(f"User '{username}' not found.")

    return app
