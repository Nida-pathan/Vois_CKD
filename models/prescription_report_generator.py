"""
PDF Report Generator for Medical Prescriptions
Generates professional medical reports from prescription data
"""

from fpdf import FPDF
from datetime import datetime
import os
import textwrap

class MedicalReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()
        self.add_page()
        self.set_font("Arial", size=12)
        
    def header(self):
        # Header background
        self.set_fill_color(13, 148, 136)  # #0d9488
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 18)
        self.set_y(10)
        self.cell(0, 10, "KidneyCompanion", ln=True, align="L")
        self.set_font("Arial", size=10)
        self.cell(0, 5, "Advanced AI Medical Analysis Report", ln=True, align="L")
        self.set_text_color(0, 0, 0)
        self.ln(10)
        
    def footer(self):
        self.set_y(-20)
        self.set_fill_color(249, 250, 251)
        self.rect(0, 277, 210, 20, 'F')
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")
        
    def add_section_title(self, title):
        self.set_font("Arial", "B", 14)
        self.set_text_color(13, 148, 136)
        self.ln(5)
        self.cell(0, 10, title, ln=True)
        self.set_draw_color(13, 148, 136)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)
        self.set_text_color(0, 0, 0)
        
    def add_patient_info(self, patient_data):
        self.add_section_title("Patient Information")
        self.set_font("Arial", size=11)
        
        # Filter fields - Whitelist only specific fields
        allowed_fields = {
            'patient_name': 'Name',
            'name': 'Name',
            'age': 'Age',
            'address': 'Address',
            'blood_type': 'Blood Type',
            'phone': 'Phone Number'
        }
        
        cols = []
        for key, label in allowed_fields.items():
            if key in patient_data and patient_data[key]:
                cols.append(f"{label}: {patient_data[key]}")
        
        # Draw in pairs
        for i in range(0, len(cols), 2):
            self.cell(95, 8, cols[i])
            if i + 1 < len(cols):
                self.cell(95, 8, cols[i+1])
            self.ln()
        self.ln(2)
        
    def add_medication_table(self, medications):
        if not medications:
            return
            
        self.add_section_title("Medications & Dosage")
        
        # Table Header
        self.set_fill_color(240, 253, 250)
        self.set_font("Arial", "B", 11)
        self.cell(10, 10, "#", 1, 0, 'C', True)
        self.cell(60, 10, "Medication Name", 1, 0, 'C', True)
        self.cell(30, 10, "Dosage", 1, 0, 'C', True)
        self.cell(30, 10, "Frequency", 1, 0, 'C', True)
        self.cell(60, 10, "Notes", 1, 1, 'C', True)
        
        # Table Body
        self.set_font("Arial", size=10)
        for i, med in enumerate(medications, 1):
            name = med.get('name', 'N/A')
            dosage = med.get('dosage', 'N/A')
            freq = med.get('frequency', 'N/A')
            notes = med.get('notes', '')
            
            # Simple height
            h = 8
            
            # Allow for potential wrap if needed, but FPDF cell is simple
            # Better to use multi_cell if notes are long, but that breaks table layout easily
            # Let's truncate notes for now to keep table clean
            display_notes = (notes[:30] + '...') if len(notes) > 30 else notes
            
            self.cell(10, h, str(i), 1, 0, 'C')
            self.cell(60, h, name, 1, 0, 'L')
            self.cell(30, h, dosage, 1, 0, 'C')
            self.cell(30, h, freq, 1, 0, 'C')
            self.cell(60, h, display_notes, 1, 1, 'L')
        self.ln(5)

    def draw_bullet_list(self, title, items):
        if not items:
            return
            
        self.add_section_title(title)
        self.set_font("Arial", size=11)
        
        if isinstance(items, str):
            # Pre-process string to add newlines before numbered items embedded in text
            # Look for patterns like " 1.", " 2." that are preceded by space and not at start of line
            import re
            # Add newline before numbers 1-9 followed by dot, if they are not at start of string
            items = re.sub(r'(?<!^)\s+(\d+\.)', r'\n\1', items)
            
            # Try to split by common markers if it's a block of text
            lines = items.split('\n')
            processed_items = []
            for line in lines:
                line = line.strip()
                # Remove common AI bullet markers
                if line.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    # Strip the marker and leading spaces
                    clean_line = re.sub(r'^(\d+\.|\-|\*|•)\s*', '', line)
                    if clean_line:
                        processed_items.append(clean_line)
                elif line:
                    processed_items.append(line)
            items = processed_items

        for item in items:
            self.set_x(15)
            # Use a standard character for bullet
            self.set_font("Arial", "B", 12)
            self.cell(5, 7, chr(149), 0, 0) 
            self.set_font("Arial", size=11)
            
            # Use MultiCell for wrapped bullet points
            self.multi_cell(0, 7, item)
            self.ln(1)
            
    def add_disclaimer(self):
        self.ln(10)
        self.set_fill_color(254, 242, 242) # Light red
        self.set_text_color(220, 38, 38) # Red
        self.set_font("Arial", "B", 10)
        self.cell(0, 8, "MEDICAL DISCLAIMER", ln=True, fill=True)
        self.set_font("Arial", "I", 9)
        disclaimer_text = ("This report is generated using AI analysis of provided prescription data. It is intended for informational and educational purposes only. "
                          "This analysis does NOT constitute medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider "
                          "with any questions you may have regarding a medical condition.")
        self.multi_cell(0, 5, disclaimer_text)
        self.set_text_color(0, 0, 0)
        
    def generate_report(self, patient_data, prescription_data, analysis_results, filename):
        # Patient Info
        self.add_patient_info(patient_data)
        
        # Medication Table
        self.add_medication_table(prescription_data.get('medications', []))
        
        # Clinical Insights
        if analysis_results.get('clinical_insights'):
            self.draw_bullet_list("Clinical Insights", analysis_results['clinical_insights'])
            
        # Risk Assessment
        if analysis_results.get('risk_assessment'):
            self.draw_bullet_list("Risk Assessment", analysis_results['risk_assessment'])
            
        # Recommendations
        if analysis_results.get('recommendations'):
            self.draw_bullet_list("Lifestyle & Care Recommendations", analysis_results['recommendations'])
            
        # Drug Interactions
        if analysis_results.get('drug_interactions'):
            self.draw_bullet_list("Potential Drug Interactions", analysis_results['drug_interactions'])
            
        # Follow-up
        if analysis_results.get('follow_up'):
            self.draw_bullet_list("Recommended Follow-up", analysis_results['follow_up'])
            
        self.add_disclaimer()
        
        # Save the PDF
        self.output(filename)
        return filename

# Example usage function
def generate_prescription_report(patient_data, prescription_data, analysis_results):
    """
    Generate a PDF report from prescription and patient data
    
    Args:
        patient_data (dict): Patient information
        prescription_data (dict): Prescription details
        analysis_results (dict): AI analysis results
        
    Returns:
        str: Path to generated PDF file
    """
    # Create reports directory if it doesn't exist
    reports_dir = "static/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    patient_name = patient_data.get('name', 'patient').replace(' ', '_')
    filename = f"{reports_dir}/{patient_name}_prescription_report_{timestamp}.pdf"
    
    # Create and generate PDF
    pdf = MedicalReportPDF()
    pdf.generate_report(patient_data, prescription_data, analysis_results, filename)
    
    return filename