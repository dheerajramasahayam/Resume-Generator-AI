import os
import json
from datetime import datetime

from flask import Blueprint, redirect, url_for, current_app, render_template
from flask_login import login_required, current_user

# Frontend template configuration
# Define template folder relative to this blueprint file's location
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
template_folder = frontend_dir
# Initialize blueprint with template folder (static is handled by main app)
pages = Blueprint('pages', __name__, template_folder=template_folder)

# Ensure all template variables are available
@pages.context_processor
def inject_template_vars():
    """Make config and other variables available to all templates"""
    config = get_template_config()
    
    # Unified template variables with JavaScript exposure
    template_vars = {
        'config': config,
        'debug': current_app.debug,
        'api_key_available': bool(config['OPENWEATHER_API_KEY']),
        'js_vars': f"""
            <script>
                window.templateVars = {json.dumps({
                    'OPENWEATHER_API_KEY': config['OPENWEATHER_API_KEY'],
                    'DEBUG': config['DEBUG'],
                    'COLOR_FEATURES': config['COLOR_FEATURES'],
                    'ENV': config['ENV'],
                    'SERVER_TIME': config['SERVER_TIME'],
                }, default=str)};
                window.debug = {str(current_app.debug).lower()};
                if (window.debug) {{
                    console.log('Template variables loaded:', window.templateVars);
                }}
            </script>
        """
    }
    
    if current_app.debug:
        print('Template variables:', {k: v for k, v in template_vars.items() if k != 'js_vars'})
    
    return template_vars

@pages.before_request
def log_request():
    """Log request details for debugging"""
    if current_app.debug:
        request_info = f"""
Request Details:
- Path: {current_app.request.path}
- User: {current_user.get_id() if current_user.is_authenticated else 'Anonymous'}
- Weather API Key: {'✓' if current_app.config.get('OPENWEATHER_API_KEY') else '✗'}
- Debug Mode: {current_app.debug}
- Server Time: {current_app.request.environ.get('SERVER_TIME', 'N/A')}
"""
        print(request_info)


def get_template_config():
    """Get common template configuration with debug info"""
    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    is_debug = current_app.debug
    current_time = datetime.now()
    
    # Format time for display and debugging
    server_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    
    config = {
        'OPENWEATHER_API_KEY': api_key,
        'DEBUG': is_debug,
        'COLOR_FEATURES': {
            'weather_enabled': bool(api_key),
            'transitions_enabled': True,
            'season_enabled': True,
            'time_based': True
        },
        'ENV': current_app.config.get('ENV', 'production'),
        'SERVER_TIME': server_time,
        'CLIENT_TIME_OFFSET': 'AUTO'  # Will be set by JavaScript
    }
    
    if is_debug:
        print(f"""
Template Configuration:
- Debug Mode: {is_debug}
- Environment: {config['ENV']}
- Weather API Key: {'✓' if api_key else '✗'}
- Color Features:
  • Weather: {'Enabled' if config['COLOR_FEATURES']['weather_enabled'] else 'Disabled'}
  • Transitions: {'Enabled' if config['COLOR_FEATURES']['transitions_enabled'] else 'Disabled'}
  • Seasonal: {'Enabled' if config['COLOR_FEATURES']['season_enabled'] else 'Disabled'}
  • Time-based: {'Enabled' if config['COLOR_FEATURES']['time_based'] else 'Disabled'}
""")
    
    return config

@pages.route('/')
def index():
    # Serve the landing page if user is not logged in
    if current_user.is_authenticated:
        return redirect(url_for('pages.profile'))
    return render_template('index.html')

@pages.route('/profile')
@login_required
def profile():
    # Render the profile template, passing the user
    return render_template('profile.html', current_user=current_user)

@pages.route('/generate_page')
@login_required
def generate_page():
     # Render the generate template, passing the user
    return render_template('generate.html', current_user=current_user)

@pages.route('/resume_display')
@login_required
def resume_display():
     # Render the resume display template, passing the user
    return render_template('resume.html', current_user=current_user)

@pages.route('/cover_letter')
@login_required
def cover_letter():
     # Render the cover letter template, passing the user
    return render_template('cover_letter.html', current_user=current_user)
