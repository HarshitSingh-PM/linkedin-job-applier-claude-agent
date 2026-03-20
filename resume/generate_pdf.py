#!/usr/bin/env python3
"""Resume PDF Generator - Creates professional 2-page PDF resumes from structured data.

Usage:
    # As a library (used by the agent):
    from generate_pdf import generate_resume
    generate_resume(data_dict, 'output.pdf')

    # Standalone test:
    python3 generate_pdf.py
"""

from fpdf import FPDF
import re
import os
import yaml


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(auto=True, margin=13)
        self.set_margins(13, 9, 13)
        self.line_height = 4.3
        self.body_size = 8.3
        self.usable_w = 210 - 13 - 13  # A4 width minus margins

    def header(self):
        pass

    def section_line(self):
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(1.8)

    def add_name(self, name):
        self.set_font('Helvetica', 'B', 19)
        self.cell(0, 8.5, name.upper(), new_x='LMARGIN', new_y='NEXT', align='C')
        self.ln(0.5)

    def add_subtitle(self, text):
        self.set_font('Helvetica', '', 8.5)
        self.cell(0, 4, text, new_x='LMARGIN', new_y='NEXT', align='C')

    def add_contact(self, text):
        self.set_font('Helvetica', '', 7.5)
        self.cell(0, 3.5, text, new_x='LMARGIN', new_y='NEXT', align='C')

    def add_contact_with_links(self, phone, email, location, linkedin=None, github=None):
        """Render contact line with clickable LinkedIn and GitHub links."""
        self.set_font('Helvetica', '', 7.5)
        line1 = f"Phone: {phone} | Email: {email} | Location: {location}"
        self.cell(0, 3.5, line1, new_x='LMARGIN', new_y='NEXT', align='C')

        if linkedin or github:
            parts = []
            if linkedin:
                parts.append(('LinkedIn: ', linkedin))
            if github:
                parts.append(('GitHub: ', github))

            total_w = 0
            for label, url in parts:
                total_w += self.get_string_width(label) + self.get_string_width(url)
            if len(parts) > 1:
                total_w += self.get_string_width(' | ')

            start_x = (self.w - total_w) / 2
            y = self.get_y()
            current_x = start_x

            for idx, (label, url) in enumerate(parts):
                if idx > 0:
                    self.set_font('Helvetica', '', 7.5)
                    sep_w = self.get_string_width(' | ')
                    self.set_xy(current_x, y)
                    self.cell(sep_w, 3.5, ' | ')
                    current_x += sep_w

                self.set_font('Helvetica', '', 7.5)
                label_w = self.get_string_width(label)
                self.set_xy(current_x, y)
                self.cell(label_w, 3.5, label)
                current_x += label_w

                self.set_font('Helvetica', 'U', 7.5)
                self.set_text_color(0, 0, 180)
                url_w = self.get_string_width(url)
                self.set_xy(current_x, y)
                self.cell(url_w, 3.5, url, link=url)
                current_x += url_w
                self.set_text_color(0, 0, 0)
                self.set_font('Helvetica', '', 7.5)

            self.set_y(y + 3.5)

    def add_section_header(self, title):
        self.ln(2)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 5, title.upper(), new_x='LMARGIN', new_y='NEXT')
        self.section_line()

    def add_experience_header(self, title, company_line, dates, location):
        if self.get_y() > 260:
            self.add_page()

        self.set_font('Helvetica', 'B', 9)
        y = self.get_y()
        self.cell(0, 4.5, title, new_x='LMARGIN', new_y='TOP')
        self.set_y(y)
        self.set_font('Helvetica', '', 8.5)
        self.cell(0, 4.5, dates, new_x='LMARGIN', new_y='NEXT', align='R')
        self.set_font('Helvetica', 'I', 8)
        y2 = self.get_y()
        self.cell(0, 4, company_line, new_x='LMARGIN', new_y='TOP')
        self.set_y(y2)
        self.cell(0, 4, location, new_x='LMARGIN', new_y='NEXT', align='R')

    def add_bullet(self, text):
        if self.get_y() + self.line_height * 2 > self.h - self.b_margin:
            self.add_page()

        self.set_font('Helvetica', '', self.body_size)
        indent = 4
        bullet_str = '- '
        bullet_w = self.get_string_width(bullet_str)

        self.set_x(self.l_margin + indent)
        self.cell(bullet_w, self.line_height, bullet_str)

        start_x = self.get_x()
        available_w = self.w - self.r_margin - start_x

        self._write_mixed_bold(text, start_x, available_w)
        self.ln(0.5)

    def _write_mixed_bold(self, text, start_x, available_w):
        parts = re.split(r'(\*\*.*?\*\*)', text)
        current_x = start_x
        current_y = self.get_y()
        page_bottom = self.h - self.b_margin

        for part in parts:
            if not part:
                continue
            if part.startswith('**') and part.endswith('**'):
                self.set_font('Helvetica', 'B', self.body_size)
                content = part[2:-2]
            else:
                self.set_font('Helvetica', '', self.body_size)
                content = part

            words = content.split(' ')
            for i, word in enumerate(words):
                if i > 0:
                    word = ' ' + word
                word_w = self.get_string_width(word)

                if current_x + word_w > self.w - self.r_margin:
                    current_y += self.line_height
                    if current_y + self.line_height > page_bottom:
                        self.add_page()
                        current_y = self.t_margin
                        page_bottom = self.h - self.b_margin
                    current_x = start_x
                    self.set_xy(current_x, current_y)
                    word = word.lstrip()
                    word_w = self.get_string_width(word)

                self.set_xy(current_x, current_y)
                self.cell(word_w, self.line_height, word)
                current_x += word_w

        self.set_y(current_y + self.line_height)

    def add_summary(self, text):
        self.set_font('Helvetica', '', self.body_size)
        self.multi_cell(0, self.line_height, text)

    def add_skills_section(self, skills_dict):
        """Render core competencies as a clean aligned grid."""
        self.set_font('Helvetica', 'B', self.body_size)
        max_label_w = max(self.get_string_width(cat + ':  ') for cat in skills_dict.keys())
        label_w = max_label_w + 2
        val_w = self.usable_w - label_w

        for category, skills in skills_dict.items():
            y_start = self.get_y()
            self.set_font('Helvetica', 'B', self.body_size)
            self.set_xy(self.l_margin, y_start)
            self.cell(label_w, self.line_height, category + ':')
            self.set_font('Helvetica', '', self.body_size)
            self.set_xy(self.l_margin + label_w, y_start)
            self.multi_cell(val_w, self.line_height, skills)
            self.ln(0.2)

    def add_education_entry(self, school, degree, date, location, details=None):
        self.set_font('Helvetica', 'B', 8.5)
        y = self.get_y()
        self.cell(0, 4.5, school, new_x='LMARGIN', new_y='TOP')
        self.set_y(y)
        self.set_font('Helvetica', '', 8)
        self.cell(0, 4.5, date, new_x='LMARGIN', new_y='NEXT', align='R')
        self.set_font('Helvetica', 'I', 8)
        y2 = self.get_y()
        self.cell(0, 3.8, degree, new_x='LMARGIN', new_y='TOP')
        self.set_y(y2)
        self.cell(0, 3.8, location, new_x='LMARGIN', new_y='NEXT', align='R')
        if details:
            self.set_font('Helvetica', '', 8)
            self.cell(0, 3.8, '- ' + details, new_x='LMARGIN', new_y='NEXT')

    def add_certification(self, cert):
        self.set_font('Helvetica', '', self.body_size)
        self.cell(0, self.line_height, '- ' + cert, new_x='LMARGIN', new_y='NEXT')


def generate_resume(data, output_path):
    """
    Generate a PDF resume from structured data.

    data = {
        'name': str,
        'subtitle': str,
        'phone': str, 'email': str, 'location': str,
        'linkedin': str, 'github': str,
        'summary': str,
        'skills': {category: skills_str, ...},
        'experience': [
            {
                'title': str,
                'company_line': str,
                'dates': str,
                'location': str,
                'bullets': [str, ...]
            }, ...
        ],
        'education': [
            {
                'school': str, 'degree': str,
                'date': str, 'location': str,
                'details': str or None
            }, ...
        ],
        'certifications': [str, ...]
    }
    """
    pdf = ResumePDF()
    pdf.add_page()

    pdf.add_name(data['name'])
    if data.get('subtitle'):
        pdf.add_subtitle(data['subtitle'])

    pdf.add_contact_with_links(
        data['phone'], data['email'], data['location'],
        data.get('linkedin'), data.get('github')
    )

    pdf.add_section_header('Professional Summary')
    pdf.add_summary(data['summary'])

    if data.get('skills'):
        pdf.add_section_header('Core Competencies')
        pdf.add_skills_section(data['skills'])

    pdf.add_section_header('Work Experience')
    for exp in data['experience']:
        pdf.add_experience_header(
            exp['title'], exp['company_line'],
            exp['dates'], exp['location']
        )
        for bullet in exp['bullets']:
            pdf.add_bullet(bullet)
        pdf.ln(1.5)

    pdf.add_section_header('Education')
    for edu in data['education']:
        pdf.add_education_entry(
            edu['school'], edu['degree'],
            edu['date'], edu['location'],
            edu.get('details')
        )

    if data.get('certifications'):
        pdf.add_section_header('Certifications')
        for cert in data['certifications']:
            pdf.add_certification(cert)

    page_count = pdf.page
    if page_count > 2:
        print(f"WARNING: {output_path} has {page_count} pages (should be 2)")

    pdf.output(output_path)
    print(f"Generated: {output_path} ({page_count} pages)")


def load_profile(profile_path=None):
    """Load candidate profile from YAML config file.
    Returns a BASE_RESUME dict compatible with generate_resume()."""
    if profile_path is None:
        # Look relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(script_dir, '..', 'config', 'profile.yaml')

    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)

    base = {
        'name': profile['name'],
        'phone': profile['phone'],
        'email': profile['email'],
        'location': profile['location'],
        'linkedin': profile.get('linkedin', ''),
        'github': profile.get('github', ''),
        'education': profile.get('education', []),
        'certifications': profile.get('certifications', []),
    }

    # Attach raw profile for agent to use during tailoring
    base['_profile'] = profile

    return base


if __name__ == '__main__':
    print("Resume PDF Generator")
    print("=" * 40)
    try:
        base = load_profile()
        print(f"Loaded profile for: {base['name']}")
        print("Profile loaded successfully. Ready for the agent to generate tailored resumes.")
    except FileNotFoundError:
        print("ERROR: config/profile.yaml not found.")
        print("Run: cp config/profile.example.yaml config/profile.yaml")
        print("Then fill in your details.")
