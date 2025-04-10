import io
import re # Import regex for cleaning
import io
import re
from flask import Blueprint, request, jsonify, current_app, make_response
from flask_login import login_required
# Import base libraries needed
from docx import Document
from fpdf import FPDF
# Import template functions and common helpers
from .export_templates import common, docx_templates, pdf_templates

export_api = Blueprint('export_api', __name__, url_prefix='/api')

@export_api.route('/export', methods=['POST'])
@login_required
def export_resume():
    data = request.json
    resume_text = data.get('resume_text')
    export_format = data.get('format') # 'docx' or 'pdf'
    template_choice = data.get('template', 'simple') # Default to 'simple'

    if not resume_text or not export_format:
        return jsonify({'error': 'Missing resume text or format.'}), 400

    # Clean the text using the common helper
    cleaned_text = common.clean_resume_text(resume_text)

    if export_format == 'docx':
        try:
            document = Document() # Create base document
            # Call the appropriate template function
            if template_choice == 'classic':
                docx_templates.generate_classic_docx(document, cleaned_text)
            elif template_choice == 'modern':
                docx_templates.generate_modern_docx(document, cleaned_text)
            else: # Default to simple
                docx_templates.generate_simple_docx(document, cleaned_text)

            # Prepare document for sending
            file_stream = io.BytesIO()
            document.save(file_stream)
            file_stream.seek(0)

            response = make_response(file_stream.read())
            response.headers.set('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response.headers.set('Content-Disposition', 'attachment', filename='resume.docx')
            return response
        except Exception as e:
            current_app.logger.error(f"Error generating DOCX: {e}")
            return jsonify({'error': 'Failed to generate DOCX file.'}), 500

    elif export_format == 'pdf':
        try:
            # Call the appropriate template function which returns PDF bytes
            if template_choice == 'classic':
                pdf_output = pdf_templates.generate_classic_pdf(cleaned_text)
            elif template_choice == 'modern':
                pdf_output = pdf_templates.generate_modern_pdf(cleaned_text)
            else: # Default to simple
                pdf_output = pdf_templates.generate_simple_pdf(cleaned_text)

            # Prepare PDF for sending
            file_stream = io.BytesIO(pdf_output)
            file_stream.seek(0)

            response = make_response(file_stream.read())
            response.headers.set('Content-Type', 'application/pdf')
            response.headers.set('Content-Disposition', 'attachment', filename='resume.pdf')
            return response
        except Exception as e:
            current_app.logger.error(f"Error generating PDF: {e}")
            return jsonify({'error': 'Failed to generate PDF file.'}), 500

    else:
        return jsonify({'error': 'Invalid export format specified.'}), 400
