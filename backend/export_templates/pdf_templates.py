from fpdf import FPDF
from .common import is_heading # Import common helper

def _setup_pdf(template_choice):
    """Helper to create PDF object and set initial styles based on template."""
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    if template_choice == 'classic':
        pdf.set_margins(left=20, top=20, right=20)
        base_font, base_size, heading_size = 'Times', 11, 13
    elif template_choice == 'modern':
        pdf.set_margins(left=15, top=15, right=15)
        base_font, base_size, heading_size = 'Helvetica', 9, 11
    else: # Simple (default)
        pdf.set_margins(left=15, top=15, right=15)
        base_font, base_size, heading_size = 'Arial', 10, 12

    pdf.set_font(base_font, size=base_size)
    # Store line height for consistency
    line_height = 5 if base_size < 11 else 6 # Adjust line height based on font size
    return pdf, base_font, base_size, heading_size, line_height

def _add_content_to_pdf(pdf, cleaned_text, base_font, base_size, heading_size, line_height):
    """Adds cleaned text to the PDF, applying heading styles using heuristic."""
    # Encode text properly for FPDF
    try:
        encoded_text = cleaned_text.encode('latin-1', 'replace').decode('latin-1')
    except Exception as e:
        print(f"Encoding error: {e}. Using fallback.")
        encoded_text = cleaned_text.encode('utf-8', 'replace').decode('utf-8', 'replace')

    for line in encoded_text.split('\n'):
        line_stripped = line.strip()
        if is_heading(line_stripped): # Use common heuristic
            pdf.set_font(base_font, 'B', size=heading_size)
            pdf.cell(0, 8, txt=line_stripped, ln=1, align='L')
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + pdf.w - pdf.l_margin - pdf.r_margin, pdf.get_y())
            pdf.ln(line_height * 0.6)
            pdf.set_font(base_font, size=base_size) # Reset font
        elif line_stripped:
            pdf.multi_cell(0, line_height, txt=line_stripped)
        else:
            pdf.ln(line_height * 0.5)

def _add_content_to_pdf_modern(pdf, cleaned_text, base_font, base_size, heading_size, line_height):
    """Adds cleaned text to the PDF, applying MODERN heading styles using heuristic."""
    try:
        encoded_text = cleaned_text.encode('latin-1', 'replace').decode('latin-1')
    except Exception:
        encoded_text = cleaned_text.encode('utf-8', 'replace').decode('utf-8', 'replace')

    for line in encoded_text.split('\n'):
        line_stripped = line.strip()
        if is_heading(line_stripped): # Use common heuristic
            pdf.set_font(base_font, 'B', size=heading_size)
            # pdf.set_text_color(46, 134, 193) # Optional color
            pdf.cell(0, 8, txt=line_stripped.upper(), ln=1, align='L') # UPPERCASE
            # pdf.set_text_color(0, 0, 0) # Reset color
            pdf.ln(line_height * 0.3) # Tight spacing
            pdf.set_font(base_font, size=base_size) # Reset font
        elif line_stripped:
            pdf.multi_cell(0, line_height, txt=line_stripped)
        else:
            pdf.ln(line_height * 0.4)

# --- Template Generation Functions ---

def generate_simple_pdf(cleaned_text):
    """Generates PDF with simple formatting."""
    pdf, bf, bs, hs, lh = _setup_pdf('simple')
    _add_content_to_pdf(pdf, cleaned_text, bf, bs, hs, lh)
    return pdf.output(dest='S')

def generate_classic_pdf(cleaned_text):
    """Generates PDF with classic formatting."""
    pdf, bf, bs, hs, lh = _setup_pdf('classic')
    _add_content_to_pdf(pdf, cleaned_text, bf, bs, hs, lh)
    return pdf.output(dest='S')

def generate_modern_pdf(cleaned_text):
    """Generates PDF with modern formatting."""
    pdf, bf, bs, hs, lh = _setup_pdf('modern')
    # Use the new modern content adder function
    _add_content_to_pdf_modern(pdf, cleaned_text, bf, bs, hs, lh)
    return pdf.output(dest='S')

# Add more template functions as needed
