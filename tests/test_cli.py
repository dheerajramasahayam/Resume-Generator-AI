import pytest
from flask.testing import FlaskCliRunner
from backend.models import User, db

def test_make_admin_command_success(runner: FlaskCliRunner, new_user, test_app):
    """Test the 'flask make-admin' command successfully makes a user admin."""
    with test_app.app_context():
        # Verify user is not admin initially
        user = db.session.get(User, new_user.id)
        assert user is not None
        assert user.is_admin is False

        # Run the command
        result = runner.invoke(args=["make-admin", new_user.username])

        # Check output and database state
        assert result.exit_code == 0
        assert f"User '{new_user.username}' is now an admin." in result.output
        user_after = db.session.get(User, new_user.id)
        assert user_after.is_admin is True

def test_make_admin_command_user_not_found(runner: FlaskCliRunner, test_app):
    """Test the 'flask make-admin' command when the user doesn't exist."""
    with test_app.app_context():
        # Run the command for a non-existent user
        result = runner.invoke(args=["make-admin", "nosuchuser"])

        # Check output
        assert result.exit_code == 0 # Command itself runs successfully
        assert "User 'nosuchuser' not found." in result.output
