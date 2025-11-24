
import os

def update_dashboard():
    file_path = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Target string (exact match from previous view_file)
    target = '''                    <div class="upload-area" onclick="document.getElementById('labUpload').click()">
                        <div class="upload-icon">
                            <i class="fas fa-cloud-upload-alt"></i>
                        </div>
                        <div class="upload-text">Upload your lab reports for AI analysis</div>
                        <div class="upload-subtext">Supports PDF, CSV, and Excel formats • Maximum file size: 10MB</div>
                        <input type="file" id="labUpload" style="display: none;" accept=".pdf,.csv,.xlsx,.xls" multiple>
                    </div>'''
    
    replacement = '''                    <div class="upload-area" onclick="window.location.href='{{ url_for('lab_analysis') }}'" style="cursor: pointer;">
                        <div class="upload-icon">
                            <i class="fas fa-cloud-upload-alt"></i>
                        </div>
                        <div class="upload-text">Upload your lab reports for AI analysis</div>
                        <div class="upload-subtext">Supports PDF format • Select Disease Type</div>
                    </div>'''
    
    if target in content:
        new_content = content.replace(target, replacement)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated dashboard link.")
    else:
        # Try a more flexible approach if exact match fails (due to whitespace)
        print("Exact match failed. Trying flexible match...")
        # We can try to find the line with onclick="document.getElementById('labUpload').click()"
        lines = content.split('\n')
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(lines):
            if 'onclick="document.getElementById(\'labUpload\').click()"' in line:
                start_idx = i
            if start_idx != -1 and '<input type="file" id="labUpload"' in line:
                end_idx = i + 1 # Include the closing div which is likely next
                if '</div>' in lines[end_idx]:
                    end_idx += 1
                break
        
        if start_idx != -1 and end_idx != -1:
            print(f"Found block from line {start_idx} to {end_idx}")
            # Construct replacement
            new_lines = lines[:start_idx] + [replacement] + lines[end_idx:]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print("Successfully updated dashboard link (flexible).")
        else:
            print("Could not find the upload block.")

if __name__ == '__main__':
    update_dashboard()
