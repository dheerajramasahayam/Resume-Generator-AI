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
    """Adds cleaned text to the PDF, applying styles based on markdown markers."""
    try:
        encoded_text = cleaned_text.encode('latin-1', 'replace').decode('latin-1')
    except Exception:
        encoded_text = cleaned_text.encode('utf-8', 'replace').decode('utf-8', 'replace')

    for line in encoded_text.split('\n'):
        line_stripped = line.strip()

        if line_stripped.startswith('### '):
            heading_text = line_stripped[4:].strip()
            pdf.set_font(base_font, 'B', size=heading_size)
            pdf.cell(0, 8, txt=heading_text.upper(), ln=1, align='L') # Uppercase heading
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + pdf.w - pdf.l_margin - pdf.r_margin, pdf.get_y()) # Line below
            pdf.ln(line_height * 0.6)
            pdf.set_font(base_font, size=base_size) # Reset font
        elif line_stripped.startswith('* '):
            item_text = line_stripped[2:].strip()
            pdf.set_x(pdf.l_margin + 5) # Indent bullet points
            pdf.multi_cell(0, line_height, txt=f"• {item_text}") # Use bullet character
            pdf.set_x(pdf.l_margin) # Reset indent
        elif '**' in line_stripped: # Basic bold handling
            pdf.set_font(base_font, 'B', size=base_size) # Set bold
            # Replace markers and print (simple approach, doesn't handle multiple bolds per line well)
            bold_text = line_stripped.replace('**', '')
            pdf.multi_cell(0, line_height, txt=bold_text)
            pdf.set_font(base_font, size=base_size) # Reset font
        elif line_stripped:
            pdf.multi_cell(0, line_height, txt=line_stripped)
        else:
            pdf.ln(line_height * 0.5)

def _add_content_to_pdf_modern(pdf, cleaned_text, base_font, base_size, heading_size, line_height):
    """Adds cleaned text to the PDF, applying MODERN styles based on markdown markers."""
    try:
        encoded_text = cleaned_text.encode('latin-1', 'replace').decode('latin-1')
    except Exception:
        encoded_text = cleaned_text.encode('utf-8', 'replace').decode('utf-8', 'replace')

    for line in encoded_text.split('\n'):
        line_stripped = line.strip()

        if line_stripped.startswith('### '):
            heading_text = line_stripped[4:].strip()
            pdf.set_font(base_font, 'B', size=heading_size)
            # pdf.set_text_color(46, 134, 193) # Optional color
            pdf.cell(0, 8, txt=heading_text.upper(), ln=1, align='L')
            # pdf.set_text_color(0, 0, 0) # Reset color
            pdf.ln(line_height * 0.3) # Tight spacing
            pdf.set_font(base_font, size=base_size)
        elif line_stripped.startswith('* '):
            item_text = line_stripped[2:].strip()
            pdf.set_x(pdf.l_margin + 4) # Slightly less indent for modern
            pdf.multi_cell(0, line_height, txt=f"- {item_text}") # Use hyphen bullet
            pdf.set_x(pdf.l_margin)
        elif '**' in line_stripped:
            pdf.set_font(base_font, 'B', size=base_size)
            bold_text = line_stripped.replace('**', '')
            pdf.multi_cell(0, line_height, txt=bold_text)
            pdf.set_font(base_font, size=base_size)
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
