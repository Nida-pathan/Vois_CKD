"""
Update patient dashboard with disease selection UI for lab upload
"""

def update_dashboard_upload_section():
    file_path = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the upload area section
    old_upload = '''                <div class="upload-area" onclick="document.getElementById('labUpload').click()">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">Upload your lab reports for AI analysis</div>
                    <div class="upload-subtext">Supports PDF, CSV, and Excel formats • Maximum file size: 10MB</div>
                    <input type="file" id="labUpload" style="display: none;" accept=".pdf,.csv,.xlsx,.xls" multiple>
                </div>'''
    
    new_upload = '''                <!-- Disease Selection -->
                <div class="disease-selection" id="diseaseSelection">
                    <h3 style="text-align: center; margin-bottom: 20px; color: #333;">Select Disease Type for Analysis</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                        <div class="disease-card" onclick="selectDisease('ckd')" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; cursor: pointer; text-align: center; color: white; transition: transform 0.3s;">
                            <i class="fas fa-kidney" style="font-size: 40px; margin-bottom: 10px;"></i>
                            <h4 style="margin-bottom: 5px;">Chronic Kidney Disease</h4>
                            <p style="font-size: 12px; opacity: 0.9;">Analyze kidney function markers</p>
                        </div>
                        <div class="disease-card" onclick="selectDisease('kidney_stone')" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 12px; cursor: pointer; text-align: center; color: white; transition: transform 0.3s;">
                            <i class="fas fa-gem" style="font-size: 40px; margin-bottom: 10px;"></i>
                            <h4 style="margin-bottom: 5px;">Kidney Stone</h4>
                            <p style="font-size: 12px; opacity: 0.9;">Calcium & uric acid analysis</p>
                        </div>
                        <div class="disease-card" onclick="selectDisease('aki')" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 12px; cursor: pointer; text-align: center; color: white; transition: transform 0.3s;">
                            <i class="fas fa-exclamation-triangle" style="font-size: 40px; margin-bottom: 10px;"></i>
                            <h4 style="margin-bottom: 5px;">Acute Kidney Injury</h4>
                            <p style="font-size: 12px; opacity: 0.9;">Rapid kidney function decline</p>
                        </div>
                        <div class="disease-card" onclick="selectDisease('esrd')" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); padding: 20px; border-radius: 12px; cursor: pointer; text-align: center; color: white; transition: transform 0.3s;">
                            <i class="fas fa-heartbeat" style="font-size: 40px; margin-bottom: 10px;"></i>
                            <h4 style="margin-bottom: 5px;">ESRD</h4>
                            <p style="font-size: 12px; opacity: 0.9;">End-stage renal disease</p>
                        </div>
                    </div>
                </div>
                
                <!-- Upload Area (shown after selection) -->
                <div class="upload-area" id="uploadArea" style="display: none; cursor: pointer;" onclick="document.getElementById('labUpload').click()">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">Upload Lab Report for <span id="selectedDiseaseName" style="color: #0d9488; font-weight: 600;"></span></div>
                    <div class="upload-subtext">PDF format • Maximum 10MB</div>
                    <input type="file" id="labUpload" style="display: none;" accept=".pdf">
                    <button onclick="changeDisease(event)" style="margin-top: 15px; background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                        <i class="fas fa-arrow-left"></i> Change Disease Type
                    </button>
                </div>'''
    
    if old_upload in content:
        content = content.replace(old_upload, new_upload)
        print("✅ Updated upload section with disease selection")
    else:
        print("⚠️  Could not find upload section to replace")
        return False
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("File saved:", file_path)
    return True

if __name__ == '__main__':
    update_dashboard_upload_section()
