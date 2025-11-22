"""
Remove old Diet & Lifestyle section from patient dashboard
"""

def remove_old_section():
    file_path = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and remove the old Diet & Lifestyle section (lines 912-965 approximately)
    new_lines = []
    skip = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        # Start skipping at old Diet & Lifestyle section
        if '<!-- Diet & Lifestyle Changes -->' in line and 'AI-Powered' not in lines[i-10:i]:
            skip = True
            print(f"Found old section at line {i+1}, removing...")
        
        # Stop skipping after closing div
        if skip:
            skip_count += 1
            if '</div>' in line and skip_count > 50:  # After enough lines
                skip = False
                skip_count = 0
                continue
        
        if not skip:
            new_lines.append(line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Removed old Diet & Lifestyle section")
    print(f"File saved: {file_path}")

if __name__ == '__main__':
    remove_old_section()
