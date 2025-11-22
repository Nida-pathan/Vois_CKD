"""
Script to make Lab Results section dynamic in patient dashboard
Replaces static fake data with actual patient metrics
"""

def update_lab_results():
    file_path = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the static Lab Results section
    old_lab_results = '''                <!-- Latest Lab Results -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-vial"></i> Latest Lab Results
                        </div>
                        <a href="#" class="card-action">View All</a>
                    </div>
                    <div class="lab-result-item">
                        <div class="lab-date">December 15, 2024</div>
                        <div class="lab-title">Complete Blood Count & Metabolic Panel</div>
                        <div class="lab-metrics">
                            <div class="lab-metric">
                                <span class="lab-metric-label">Hemoglobin:</span>
                                <span class="lab-metric-value">14.2 g/dL</span>
                            </div>
                            <div class="lab-metric">
                                <span class="lab-metric-label">WBC:</span>
                                <span class="lab-metric-value">6,500/μL</span>
                            </div>
                            <div class="lab-metric">
                                <span class="lab-metric-label">Platelets:</span>
                                <span class="lab-metric-value">250,000/μL</span>
                            </div>
                            <div class="lab-metric">
                                <span class="lab-metric-label">Sodium:</span>
                                <span class="lab-metric-value">140 mEq/L</span>
                            </div>
                            <div class="lab-metric">
                                <span class="lab-metric-label">Potassium:</span>
                                <span class="lab-metric-value">4.2 mEq/L</span>
                            </div>
                        </div>
                    </div>
                    <div class="lab-result-item">
                        <div class="lab-date">November 20, 2024</div>
                        <div class="lab-title">Kidney Function Panel</div>
                        <div class="lab-metrics">
                            <div class="lab-metric">
                                <span class="lab-metric-label">BUN:</span>
                                <span class="lab-metric-value">18 mg/dL</span>
                            </div>
                            <div class="lab-metric">
                                <span class="lab-metric-label">Creatinine:</span>
                                <span class="lab-metric-value">1.1 mg/dL</span>
                            </div>
                            <div class="lab-metric">
                                <span class="lab-metric-label">eGFR:</span>
                                <span class="lab-metric-value">85 mL/min</span>
                            </div>
                            <div class="lab-metric">
                                <span class="lab-metric-label">Uric Acid:</span>
                                <span class="lab-metric-value">5.5 mg/dL</span>
                            </div>
                        </div>
                    </div>
                </div>'''
    
    new_lab_results = '''                <!-- Latest Lab Results -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-vial"></i> Latest Lab Results
                        </div>
                        <a href="#" class="card-action">View All</a>
                    </div>
                    
                    {% if dashboard.current_metrics.hemoglobin != 'N/A' or dashboard.current_metrics.sodium != 'N/A' %}
                        <div class="lab-result-item">
                            <div class="lab-date">Current Values</div>
                            <div class="lab-title">Complete Blood Count & Metabolic Panel</div>
                            <div class="lab-metrics">
                                {% if dashboard.current_metrics.hemoglobin != 'N/A' %}
                                <div class="lab-metric">
                                    <span class="lab-metric-label">Hemoglobin:</span>
                                    <span class="lab-metric-value">{{ dashboard.current_metrics.hemoglobin }} g/dL</span>
                                </div>
                                {% endif %}
                                {% if dashboard.current_metrics.sodium != 'N/A' %}
                                <div class="lab-metric">
                                    <span class="lab-metric-label">Sodium:</span>
                                    <span class="lab-metric-value">{{ dashboard.current_metrics.sodium }} mEq/L</span>
                                </div>
                                {% endif %}
                                {% if dashboard.current_metrics.potassium != 'N/A' %}
                                <div class="lab-metric">
                                    <span class="lab-metric-label">Potassium:</span>
                                    <span class="lab-metric-value">{{ dashboard.current_metrics.potassium }} mEq/L</span>
                                </div>
                                {% endif %}
                            </div>
                        </div>
                    {% endif %}
                    
                    {% if dashboard.current_metrics.serum_creatinine != 'N/A' or dashboard.current_metrics.blood_urea != 'N/A' %}
                        <div class="lab-result-item">
                            <div class="lab-date">Current Values</div>
                            <div class="lab-title">Kidney Function Panel</div>
                            <div class="lab-metrics">
                                {% if dashboard.current_metrics.blood_urea != 'N/A' %}
                                <div class="lab-metric">
                                    <span class="lab-metric-label">BUN:</span>
                                    <span class="lab-metric-value">{{ dashboard.current_metrics.blood_urea }} mg/dL</span>
                                </div>
                                {% endif %}
                                {% if dashboard.current_metrics.serum_creatinine != 'N/A' %}
                                <div class="lab-metric">
                                    <span class="lab-metric-label">Creatinine:</span>
                                    <span class="lab-metric-value">{{ dashboard.current_metrics.serum_creatinine }} mg/dL</span>
                                </div>
                                {% endif %}
                                {% if dashboard.current_metrics.egfr != 'N/A' %}
                                <div class="lab-metric">
                                    <span class="lab-metric-label">eGFR:</span>
                                    <span class="lab-metric-value">{{ dashboard.current_metrics.egfr }} mL/min</span>
                                </div>
                                {% endif %}
                            </div>
                        </div>
                    {% endif %}
                    
                    {% if dashboard.current_metrics.hemoglobin == 'N/A' and dashboard.current_metrics.sodium == 'N/A' and dashboard.current_metrics.serum_creatinine == 'N/A' %}
                        <div style="text-align: center; padding: 40px 20px; color: #666;">
                            <i class="fas fa-file-medical" style="font-size: 48px; margin-bottom: 20px; color: #0d9488;"></i>
                            <h3 style="margin-bottom: 15px; color: #333;">No Lab Results Yet</h3>
                            <p style="margin-bottom: 20px;">Upload your lab reports to see your kidney health analysis.</p>
                            <button onclick="document.getElementById('labUpload').click()" 
                                    style="background: #0d9488; color: white; border: none; padding: 12px 24px; 
                                           border-radius: 8px; cursor: pointer; font-weight: 500;">
                                <i class="fas fa-upload"></i> Upload Lab Report
                            </button>
                        </div>
                    {% endif %}
                </div>'''
    
    if old_lab_results in content:
        content = content.replace(old_lab_results, new_lab_results)
        print("✅ Updated Lab Results section")
    else:
        print("⚠️  Could not find exact Lab Results section to replace")
        print("   The section may have already been modified")
        return False
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Lab Results section is now fully dynamic!")
    print("File saved:", file_path)
    return True

if __name__ == '__main__':
    update_lab_results()
