from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import google.generativeai as genai
# Import NLTK stuff
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
import string
# Import get_profile function from profile_api
from .profile_api import get_profile

generation_api = Blueprint('generation_api', __name__, url_prefix='/api')

@generation_api.route('/generate', methods=['POST'])
@login_required
def generate_resume():
    job_description = request.json.get('job_description')
    if not job_description:
        return jsonify({'error': 'Job description is required.'}), 400

    # Fetch user profile data using the imported function
    profile_data_response = get_profile()
    # Check if the response indicates an error or is not JSON
    if not isinstance(profile_data_response, tuple) or profile_data_response[1] != 200:
         # Handle potential errors from get_profile if it were more complex
         # For now, assume it returns JSON even on error, or handle specific status codes
         try:
             profile_data = profile_data_response.get_json()
         except: # If it's not a Response object or doesn't have get_json
             current_app.logger.error("Failed to get profile data for generation.")
             return jsonify({'error': 'Could not retrieve profile data.'}), 500
    else:
         profile_data = profile_data_response[0].get_json() # get_profile returns (jsonify_obj, 200)

    # Basic check if profile seems empty
    if not profile_data.get('personal_info') and not profile_data.get('experiences'):
         return jsonify({'error': 'Please complete your profile before generating a resume.'}), 400

    # --- Construct Prompt for Gemini ---
    # (Keep the prompt construction logic here)
    prompt_parts = ["Generate a professional resume tailored for the following job description, using the candidate's details provided below."]
    prompt_parts.append("\n--- JOB DESCRIPTION ---")
    prompt_parts.append(job_description)
    prompt_parts.append("\n--- CANDIDATE PROFILE ---")
    pi = profile_data.get('personal_info', {})
    prompt_parts.append("\n**Personal Information:**")
    if pi.get('full_name'): prompt_parts.append(f"- Name: {pi['full_name']}")
    # ... (rest of prompt construction as before) ...
    if pi.get('phone_number'): prompt_parts.append(f"- Phone: {pi['phone_number']}")
    if pi.get('email_address'): prompt_parts.append(f"- Email: {pi['email_address']}")
    if pi.get('location'): prompt_parts.append(f"- Location: {pi['location']}")
    if pi.get('linkedin_url'): prompt_parts.append(f"- LinkedIn: {pi['linkedin_url']}")
    if pi.get('portfolio_url'): prompt_parts.append(f"- Portfolio: {pi['portfolio_url']}")
    if pi.get('target_job'): prompt_parts.append(f"- Target Role/Summary Hint: {pi['target_job']}")

    if profile_data.get('experiences'):
            prompt_parts.append("\n**Work Experience:**")
            for exp in profile_data['experiences']:
                prompt_parts.append(f"- **{exp['job_title']}** at {exp['company_name']} ({exp.get('location', 'N/A')})")
                prompt_parts.append(f"  {exp.get('start_date', '')} - {exp.get('end_date', '')}")
                if exp.get('description'):
                    # Perform replacement outside the f-string expression
                    formatted_desc = exp['description'].replace('\n', '\n    - ')
                    prompt_parts.append(f"  Responsibilities/Achievements:\n    - {formatted_desc}")

    # Correct indentation for the following blocks
    if profile_data.get('educations'):
        prompt_parts.append("\n**Education:**")
        for edu in profile_data['educations']:
            prompt_parts.append(f"- **{edu['degree_name']}** in {edu.get('major', 'N/A')}")
            prompt_parts.append(f"  {edu.get('institution_name', 'N/A')} ({edu.get('location', 'N/A')})")
            if edu.get('graduation_date'): prompt_parts.append(f"  Graduated: {edu['graduation_date']}")

    if profile_data.get('skills'):
        prompt_parts.append("\n**Skills:**")
        prompt_parts.append("- " + ", ".join([skill['skill_name'] for skill in profile_data['skills']]))

    if profile_data.get('projects'):
        prompt_parts.append("\n**Projects:**")
        for proj in profile_data['projects']:
            prompt_parts.append(f"- **{proj['project_name']}**")
            if proj.get('description'): prompt_parts.append(f"  {proj['description']}")
            if proj.get('link'): prompt_parts.append(f"  Link: {proj['link']}")

    prompt_parts.append("\n--- INSTRUCTIONS ---")
    prompt_parts.append("Please format the output as a standard resume, including sections like Summary/Objective (generate one if appropriate), Experience, Education, Skills, and Projects. Focus on highlighting experiences and skills relevant to the job description.")
    prompt_parts.append("IMPORTANT: Only output the resume text itself, starting directly with the candidate's name or summary. Do not include any introductory phrases, explanations, or concluding remarks before or after the resume content.")

    full_prompt = "\n".join(prompt_parts)

    # --- Call Gemini API ---
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        current_app.logger.error("GEMINI_API_KEY not configured.")
        return jsonify({'error': 'API key not configured.'}), 500

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')
        response = model.generate_content(full_prompt)
        generated_text = response.text
    except Exception as e:
        current_app.logger.error(f"Gemini API error: {e}")
        return jsonify({'error': f'Failed to generate resume via API: {e}'}), 500

    return jsonify({'resume_text': generated_text}), 200


@generation_api.route('/extract_keywords', methods=['POST'])
@login_required
def extract_keywords():
    data = request.json
    job_description = data.get('job_description')

    if not job_description:
        return jsonify({'error': 'Missing job description.'}), 400

    try:
        # --- Basic Keyword Extraction using NLTK ---
        tokens = word_tokenize(job_description.lower())
        stop_words = set(stopwords.words('english'))
        punctuation = set(string.punctuation)
        filtered_tokens = [
            word for word in tokens
            if word.isalpha() and word not in stop_words and word not in punctuation and len(word) > 2
        ]
        lemmatizer = WordNetLemmatizer()
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
        word_counts = Counter(lemmatized_tokens)
        top_keywords = [word for word, count in word_counts.most_common(15)]

        return jsonify({'keywords': top_keywords}), 200

    except Exception as e:
        current_app.logger.error(f"Error extracting keywords: {e}")
        return jsonify({'keywords': [], 'warning': 'Could not extract keywords.'}), 200


@generation_api.route('/generate_cover_letter', methods=['POST'])
@login_required
def generate_cover_letter():
    data = request.json
    job_description = data.get('job_description')
    company_name = data.get('company_name')
    hiring_manager = data.get('hiring_manager') # Optional
    additional_notes = data.get('additional_notes') # Optional

    if not job_description or not company_name:
        return jsonify({'error': 'Job description and company name are required.'}), 400

    # Fetch user profile data
    profile_data_response = get_profile()
    if not isinstance(profile_data_response, tuple) or profile_data_response[1] != 200:
         try:
             profile_data = profile_data_response.get_json()
         except:
             current_app.logger.error("Failed to get profile data for cover letter.")
             return jsonify({'error': 'Could not retrieve profile data.'}), 500
    else:
         profile_data = profile_data_response[0].get_json()

    # Check if profile seems empty (at least name needed)
    if not profile_data.get('personal_info') or not profile_data.get('personal_info').get('full_name'):
         return jsonify({'error': 'Please complete your profile (at least name) before generating a cover letter.'}), 400

    # --- Construct Prompt for Gemini ---
    prompt_parts = [
        f"Generate a professional cover letter for a position based on the provided job description at {company_name}.",
        "The letter should be tailored using the candidate's profile details below.",
        "Address it appropriately (e.g., 'Dear Hiring Manager,' or use the provided name)." if not hiring_manager else f"Address it to {hiring_manager}.",
        "Structure it with an introduction, body paragraphs highlighting relevant skills/experience from the profile that match the job description, and a conclusion expressing enthusiasm and call to action.",
        "Maintain a professional and enthusiastic tone."
    ]
    if additional_notes:
        prompt_parts.append(f"Incorporate the following points if relevant: {additional_notes}")

    prompt_parts.append("\n--- JOB DESCRIPTION ---")
    prompt_parts.append(job_description)
    prompt_parts.append("\n--- CANDIDATE PROFILE ---")
    # Include relevant profile parts (similar to resume prompt)
    pi = profile_data.get('personal_info', {})
    prompt_parts.append(f"\nName: {pi.get('full_name', 'N/A')}")
    # Include key skills and maybe brief summary of experience types if available
    if profile_data.get('skills'):
        skills_str = ", ".join([skill['skill_name'] for skill in profile_data['skills']])
        prompt_parts.append(f"Key Skills: {skills_str}")
    if profile_data.get('experiences'):
         exp_titles = ", ".join(list(set([exp['job_title'] for exp in profile_data['experiences']]))) # Unique job titles
         prompt_parts.append(f"Relevant Experience Areas: {exp_titles}")
    # Add more profile details as needed for better context

    prompt_parts.append("\n--- INSTRUCTIONS ---")
    prompt_parts.append("Generate only the cover letter text, starting with the salutation (e.g., 'Dear ...'). Do not include any introductory or concluding remarks outside the letter itself.")

    full_prompt = "\n".join(prompt_parts)

    # --- Call Gemini API ---
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        current_app.logger.error("GEMINI_API_KEY not configured.")
        return jsonify({'error': 'API key not configured.'}), 500

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25') # Use same model for consistency
        response = model.generate_content(full_prompt)
        generated_text = response.text
    except Exception as e:
        current_app.logger.error(f"Gemini API error (Cover Letter): {e}")
        return jsonify({'error': f'Failed to generate cover letter via API: {e}'}), 500

    return jsonify({'cover_letter_text': generated_text}), 200
