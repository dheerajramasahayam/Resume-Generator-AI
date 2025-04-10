from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
# Adjust imports based on new location relative to models/app
from .models import db, User, PersonalInfo, Experience, Education, Skill, Project

profile_api = Blueprint('profile_api', __name__, url_prefix='/api') # Add prefix

@profile_api.route('/get_profile', methods=['GET'])
@login_required
def get_profile():
    user = current_user
    personal_info = user.personal_info
    experiences = user.experiences.order_by(Experience.id).all()
    educations = user.educations.order_by(Education.id).all()
    skills = user.skills.order_by(Skill.id).all()
    projects = user.projects.order_by(Project.id).all()

    profile_data = {
        'username': user.username, # Add username here
        'personal_info': {
            'full_name': personal_info.full_name if personal_info else '',
            'phone_number': personal_info.phone_number if personal_info else '',
            'email_address': personal_info.email_address if personal_info else '',
            'linkedin_url': personal_info.linkedin_url if personal_info else '',
            'portfolio_url': personal_info.portfolio_url if personal_info else '',
            'location': personal_info.location if personal_info else '',
            'target_job': personal_info.target_job if personal_info else '',
        } if personal_info else {},
        'experiences': [{'id': exp.id, 'job_title': exp.job_title, 'company_name': exp.company_name, 'location': exp.location, 'start_date': exp.start_date, 'end_date': exp.end_date, 'description': exp.description} for exp in experiences],
        'educations': [{'id': edu.id, 'degree_name': edu.degree_name, 'major': edu.major, 'institution_name': edu.institution_name, 'location': edu.location, 'graduation_date': edu.graduation_date} for edu in educations],
        'skills': [{'id': skill.id, 'skill_name': skill.skill_name} for skill in skills],
        'projects': [{'id': proj.id, 'project_name': proj.project_name, 'description': proj.description, 'link': proj.link} for proj in projects],
    }
    # Return just the JSON data, status code defaults to 200
    return jsonify(profile_data)

@profile_api.route('/save_profile', methods=['POST'])
@login_required
def save_profile():
    data = request.json
    user = current_user

    # --- Update Personal Info ---
    personal_data = data.get('personal_info', {})
    personal_info = user.personal_info
    if not personal_info:
        personal_info = PersonalInfo(user_id=user.id)
        db.session.add(personal_info)
    personal_info.full_name = personal_data.get('full_name')
    personal_info.phone_number = personal_data.get('phone_number')
    personal_info.email_address = personal_data.get('email_address')
    personal_info.linkedin_url = personal_data.get('linkedin_url')
    personal_info.portfolio_url = personal_data.get('portfolio_url')
    personal_info.location = personal_data.get('location')
    personal_info.target_job = personal_data.get('target_job')

    # --- Update Experiences (Replace existing ones for simplicity) ---
    Experience.query.filter_by(user_id=user.id).delete()
    experiences_data = data.get('experiences', [])
    for exp_data in experiences_data:
        if exp_data.get('job_title'):
            exp = Experience(
                job_title=exp_data.get('job_title'),
                company_name=exp_data.get('company_name'),
                location=exp_data.get('location'),
                start_date=exp_data.get('start_date'),
                end_date=exp_data.get('end_date'),
                description=exp_data.get('description'),
                user_id=user.id
            )
            db.session.add(exp)

    # --- Update Educations (Replace existing) ---
    Education.query.filter_by(user_id=user.id).delete()
    educations_data = data.get('educations', [])
    for edu_data in educations_data:
         if edu_data.get('degree_name'):
            edu = Education(
                degree_name=edu_data.get('degree_name'),
                major=edu_data.get('major'),
                institution_name=edu_data.get('institution_name'),
                location=edu_data.get('location'),
                graduation_date=edu_data.get('graduation_date'),
                user_id=user.id
            )
            db.session.add(edu)

    # --- Update Skills (Replace existing) ---
    Skill.query.filter_by(user_id=user.id).delete()
    skills_data = data.get('skills', [])
    for skill_data in skills_data:
        if skill_data.get('skill_name'):
            skill = Skill(skill_name=skill_data.get('skill_name'), user_id=user.id)
            db.session.add(skill)

    # --- Update Projects (Replace existing) ---
    Project.query.filter_by(user_id=user.id).delete()
    projects_data = data.get('projects', [])
    for proj_data in projects_data:
        if proj_data.get('project_name'):
            proj = Project(
                project_name=proj_data.get('project_name'),
                description=proj_data.get('description'),
                link=proj_data.get('link'),
                user_id=user.id
            )
            db.session.add(proj)

    try:
        db.session.commit()
        return jsonify({'message': 'Profile saved successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving profile for user {user.id}: {e}")
        # Standardized JSON error response
        return jsonify({'error': f'An unexpected error occurred while saving the profile: {e}'}), 500
