import re

# List of potential headings for detection
POTENTIAL_HEADINGS = [
    "Experience", "Work Experience", "Employment History",
    "Education",
    "Skills", "Technical Skills", "Professional Skills",
    "Projects",
    "Summary", "Objective", "Profile",
    "Contact", "Personal Information"
]

def clean_resume_text(resume_text):
    """Cleans only excessive whitespace, preserves markdown for parsing."""
    if not resume_text:
        return ""
    # Collapse multiple blank lines but keep single ones
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', resume_text.strip()) # 3+ newlines -> 2
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned) # 2 newlines -> 2 (ensure consistency)
    return cleaned

# Keep is_heading for now as a fallback or helper, but parsing should primarily use markers
def is_heading(line):
    """Basic heuristic to check if a line is likely a section heading."""
    line_stripped = line.strip()
    if not line_stripped:
        return False
    # Check if it ends with ':' or contains common heading keywords (case-insensitive)
    # Limit length check to avoid matching long paragraphs
    if len(line_stripped) < 50 and (line_stripped.endswith(':') or \
       any(h.lower() in line_stripped.lower() for h in POTENTIAL_HEADINGS)):
        # Further check: ensure it mostly contains words from the potential headings list or is short
        words_in_line = set(line_stripped.lower().replace(':', '').split())
        heading_words = set(word.lower() for h in POTENTIAL_HEADINGS for word in h.split())
        if len(words_in_line.intersection(heading_words)) > 0 or len(words_in_line) <= 3:
             return True
    return False
