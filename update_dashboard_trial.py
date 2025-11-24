
import os
import re

def update_dashboard():
    file_path = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We look for the trial section start
    start_marker = '<div class="trial-section">'
    end_marker = '<!-- Patient Information -->'
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        # Extract the section to verify
        section = content[start_idx:end_idx]
        
        # New content
        new_section = '''<div class="trial-section">
                    <div class="trial-header">
                        <div class="trial-title">
                            <i class="fas fa-flask"></i> Lab Report Analysis
                        </div>
                    </div>
                    <div class="upload-area" onclick="window.location.href='{{ url_for('lab_analysis') }}'" style="cursor: pointer;">
                        <div class="upload-icon">
                            <i class="fas fa-cloud-upload-alt"></i>
                        </div>
                        <div class="upload-text">Upload your lab reports for AI analysis</div>
                        <div class="upload-subtext">Supports PDF format • Select Disease Type</div>
                    </div>
                </div>
                
                '''
        
        # Replace
        new_content = content[:start_idx] + new_section + content[end_idx:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated dashboard trial section.")
    else:
        print("Could not find the trial section block.")

if __name__ == '__main__':
    update_dashboard()
