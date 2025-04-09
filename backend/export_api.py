import io
import re # Import regex for cleaning
from flask import Blueprint, request, jsonify, current_app, make_response
from flask_login import login_required
# Import export libraries
from docx import Document
from docx.shared import Pt
from fpdf import FPDF

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

    # --- Clean basic markdown from the text ---
    # Remove starting bullets/asterisks and leading/trailing whitespace
    cleaned_text = re.sub(r'^\s*[\*\-]\s+', '', resume_text.strip(), flags=re.MULTILINE)
    cleaned_text = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_text) # Remove bold markers
    cleaned_text = re.sub(r'__(.*?)__', r'\1', cleaned_text) # Remove underline markers
    cleaned_text = re.sub(r'\*(.*?)\*', r'\1', cleaned_text) # Remove italic markers
    # Collapse multiple blank lines into one
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)

    if export_format == 'docx':
        try:
            # --- DOCX Template Logic ---
            document = Document()
            # Set default font based on template
            style = document.styles['Normal']
            font = style.font
            if template_choice == 'classic':
                font.name = 'Times New Roman'
                font.size = Pt(12)
            elif template_choice == 'modern':
                font.name = 'Arial' # Example for modern
                font.size = Pt(10)
            else: # Simple (default)
                font.name = 'Calibri'
                font.size = Pt(11)

            # Add cleaned text with basic paragraph spacing
            for paragraph_text in cleaned_text.split('\n'): # Use cleaned_text
                 if paragraph_text.strip():
                    paragraph = document.add_paragraph(paragraph_text.strip())
                    paragraph_format = paragraph.paragraph_format
                    paragraph_format.space_after = Pt(6)
                 elif not paragraph_text.strip() and len(document.paragraphs) > 0 and document.paragraphs[-1].text.strip():
                     last_para_format = document.paragraphs[-1].paragraph_format
                     if last_para_format.space_after is None or last_para_format.space_after < Pt(10):
                         document.add_paragraph()

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
            # --- PDF Template Logic ---
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_margins(left=15, top=15, right=15)

            if template_choice == 'classic':
                base_font, base_size, heading_size = 'Times', 11, 13
            elif template_choice == 'modern':
                base_font, base_size, heading_size = 'Helvetica', 9, 11
            else: # Simple (default)
                base_font, base_size, heading_size = 'Arial', 10, 12

            pdf.set_font(base_font, size=base_size)
            potential_headings = ["Experience", "Education", "Skills", "Projects", "Summary", "Objective", "Contact", "Personal Information"]
            # Use cleaned_text for PDF generation as well
            encoded_text = cleaned_text.encode('latin-1', 'replace').decode('latin-1')

            for line in encoded_text.split('\n'):
                line_stripped = line.strip()
                is_heading = False
                if line_stripped.endswith(':') or any(h.lower() in line_stripped.lower() for h in potential_headings if len(line_stripped) < 40):
                     if any(h.lower() in line_stripped.lower() for h in potential_headings):
                         is_heading = True

                if is_heading:
                    pdf.set_font(base_font, 'B', size=heading_size)
                    pdf.cell(0, 8, txt=line_stripped, ln=1)
                    # Add a line below the heading
                    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + pdf.w - pdf.l_margin - pdf.r_margin, pdf.get_y())
                    pdf.ln(2) # Add a small space after the line
                    pdf.set_font(base_font, size=base_size) # Reset font
                elif line_stripped:
                    pdf.multi_cell(0, 5, txt=line_stripped)
                else:
                    pdf.ln(3)

            # Prepare PDF for sending
            pdf_output = pdf.output(dest='S')
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
