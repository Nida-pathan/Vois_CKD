#!/usr/bin/env python3
"""
Manual file assembly approach to reorganize dashboard.
This reads the backup, makes precise modifications, and writes a new file.
"""

# Read the backup file
with open('templates/doctor_dashboard_backup.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Convert to list for easier manipulation
output_lines = []

# Track which section we're in
in_container_css = False
in_grid_css = False
in_body_section = False
in_profile_card = False
in_sidebar = False
skip_until_line = -1

for i, line in enumerate(lines):
    # Skip lines if we're in a section we're replacing
    if i < skip_until_line:
        continue
    
    # 1. Replace dashboard-container CSS (around line 57-60)
    if '.dashboard-container {' in line and not in_container_css:
        in_container_css = True
        output_lines.append(line)
        # Skip the old CSS and add new
        output_lines.append('            max-width: 1600px;\n')
        output_lines.append('            margin: 0 auto;\n')
        output_lines.append('            display: flex;\n')
        output_lines.append('            gap: 20px;\n')
        output_lines.append('        }\n')
        output_lines.append('\n')
        output_lines.append('        /* Left Sidebar */\n')
        output_lines.append('        .left-sidebar {\n')
        output_lines.append('            width: 250px;\n')
        output_lines.append('            flex-shrink: 0;\n')
        output_lines.append('        }\n')
        output_lines.append('\n')
        output_lines.append('        .main-wrapper {\n')
        output_lines.append('            flex: 1;\n')
        output_lines.append('            min-width: 0;\n')
        # Skip next 3 lines (old container CSS)
        skip_until_line = i + 4
        continue
    
    # 2. Replace dashboard-grid CSS (around line 195-200)
    if '/* Main Content Grid */' in line and not in_grid_css:
        in_grid_css = True
        output_lines.append(line)
        output_lines.append('        .dashboard-grid {\n')
        output_lines.append('            display: grid;\n')
        output_lines.append('            grid-template-columns: 1fr;\n')
        output_lines.append('            gap: 25px;\n')
        output_lines.append('            margin-bottom: 30px;\n')
        # Skip next 6 lines (old grid CSS)
        skip_until_line = i + 7
        continue
    
    # 3. Replace body opening and top bar (around line 820-865)
    if '<body>' in line and not in_body_section:
        in_body_section = True
        output_lines.append(line)
        output_lines.append('    <div class="dashboard-container">\n')
        output_lines.append('        <!-- Left Sidebar with Menu -->\n')
        output_lines.append('        <div class="left-sidebar">\n')
        output_lines.append('            <div class="nav-card">\n')
        output_lines.append('                <div class="sidebar-title">Menu</div>\n')
        output_lines.append('                <div class="nav-list">\n')
        output_lines.append('                    <a href="{{ url_for(\'doctor_dashboard\') }}" class="nav-item active">\n')
        output_lines.append('                        <i class="fas fa-th-large"></i>\n')
        output_lines.append('                        <span>Dashboard</span>\n')
        output_lines.append('                    </a>\n')
        output_lines.append('                    <a href="{{ url_for(\'appointments\') }}" class="nav-item">\n')
        output_lines.append('                        <i class="fas fa-calendar-alt"></i>\n')
        output_lines.append('                        <span>Appointments</span>\n')
        output_lines.append('                    </a>\n')
        output_lines.append('                    <a href="{{ url_for(\'messages\') }}" class="nav-item">\n')
        output_lines.append('                        <i class="fas fa-comments"></i>\n')
        output_lines.append('                        <span>Messages</span>\n')
        output_lines.append('                    </a>\n')
        output_lines.append('                    <a href="{{ url_for(\'prescriptions\') }}" class="nav-item">\n')
        output_lines.append('                        <i class="fas fa-file-prescription"></i>\n')
        output_lines.append('                        <span>Prescriptions</span>\n')
        output_lines.append('                    </a>\n')
        output_lines.append('                    <a href="{{ url_for(\'lab_results\') }}" class="nav-item">\n')
        output_lines.append('                        <i class="fas fa-flask"></i>\n')
        output_lines.append('                        <span>Lab Results</span>\n')
        output_lines.append('                    </a>\n')
        output_lines.append('                    <a href="{{ url_for(\'education\') }}" class="nav-item">\n')
        output_lines.append('                        <i class="fas fa-book-medical"></i>\n')
        output_lines.append('                        <span>Education</span>\n')
        output_lines.append('                    </a>\n')
        output_lines.append('                </div>\n')
        output_lines.append('            </div>\n')
        output_lines.append('        </div>\n')
        output_lines.append('\n')
        output_lines.append('        <!-- Main Content Wrapper -->\n')
        output_lines.append('        <div class="main-wrapper">\n')
        output_lines.append('            <!-- Top Bar -->\n')
        output_lines.append('            <div class="top-bar">\n')
        output_lines.append('                <div class="logo">\n')
        output_lines.append('                    <div class="logo-icon">\n')
        output_lines.append('                        <i class="fas fa-heartbeat"></i>\n')
        output_lines.append('                    </div>\n')
        output_lines.append('                    <span>CKD Diagnostic System</span>\n')
        output_lines.append('                </div>\n')
        output_lines.append('\n')
        output_lines.append('                <div class="top-bar-right">\n')
        output_lines.append('                    <div class="search-bar">\n')
        output_lines.append('                        <i class="fas fa-search"></i>\n')
        output_lines.append('                        <input type="text" id="patientSearch" placeholder="Search patients..." onkeyup="filterPatients()">\n')
        output_lines.append('                    </div>\n')
        output_lines.append('\n')
        output_lines.append('                    <div class="top-icon-btn" onclick="toggleTheme()" title="Toggle Dark Mode">\n')
        output_lines.append('                        <i class="fas fa-moon" id="themeIcon"></i>\n')
        output_lines.append('                    </div>\n')
        output_lines.append('\n')
        output_lines.append('                    <div class="top-icon-btn" title="Notifications">\n')
        output_lines.append('                        <i class="fas fa-bell"></i>\n')
        output_lines.append('                        <span class="notification-badge"></span>\n')
        output_lines.append('                    </div>\n')
        output_lines.append('\n')
        output_lines.append('                    <div class="profile-icon" onclick="window.location.href=\'{{ url_for(\'logout\') }}\'" title="Logout">\n')
        output_lines.append('                        <i class="fas fa-sign-out-alt"></i>\n')
        output_lines.append('                    </div>\n')
        output_lines.append('                </div>\n')
        output_lines.append('            </div>\n')
        output_lines.append('\n')
        output_lines.append('            <!-- Doctor Name Bar -->\n')
        output_lines.append('            <div class="welcome-text" style="background: var(--glass-bg); padding: 15px 20px; border-radius: var(--border-radius-md); margin-bottom: 20px; margin-top: 20px; border: 1px solid var(--glass-border); backdrop-filter: blur(10px); box-shadow: var(--shadow-light);">\n')
        output_lines.append('                Welcome, <span>Dr. {{ current_user.username }}</span>\n')
        output_lines.append('            </div>\n')
        output_lines.append('\n')
        output_lines.append('            <!-- Hidden input for file upload -->\n')
        output_lines.append('            <input type="file" id="pdfUpload" accept=".pdf" style="display: none;" onchange="uploadPDF(this)">\n')
        output_lines.append('\n')
        # Skip until stats-grid (around line 867)
        for j in range(i+1, len(lines)):
            if '<!-- Stats Grid -->' in lines[j]:
                skip_until_line = j
                break
        continue
    
    # 4. Modify profile card to add action buttons (around line 896-919)
    if '<!-- Profile Card -->' in line and not in_profile_card:
        in_profile_card = True
        output_lines.append('                <!-- Profile Card with Action Buttons -->\n')
        # Find the closing </div> of profile-header
        for j in range(i+1, min(i+30, len(lines))):
            output_lines.append(lines[j])
            if '</div>' in lines[j] and 'stats-pills' in ''.join(lines[max(0,j-10):j]):
                # Add action buttons before closing profile-header
                output_lines.append('                        </div>\n')
                output_lines.append('                        <div class="actions-group" style="display: flex; gap: 10px; margin-left: auto;">\n')
                output_lines.append('                            <button onclick="window.location.href=\'{{ url_for(\'add_patient\') }}\'" class="btn-action">\n')
                output_lines.append('                                <i class="fas fa-user-plus"></i> Add Patient\n')
                output_lines.append('                            </button>\n')
                output_lines.append('                            <button onclick="document.getElementById(\'pdfUpload\').click()" class="btn-action">\n')
                output_lines.append('                                <i class="fas fa-file-upload"></i> Upload Prescription\n')
                output_lines.append('                            </button>\n')
                output_lines.append('                        </div>\n')
                skip_until_line = j + 2
                break
        continue
    
    # 5. Remove right sidebar (around line 981-1062)
    if '<!-- Right Sidebar -->' in line and not in_sidebar:
        in_sidebar = True
        # Skip until we find the closing </div> for dashboard-grid
        for j in range(i+1, len(lines)):
            if '</div>' in lines[j] and j > i + 80:  # The sidebar is about 80+ lines
                # Don't skip this closing div, we need it
                skip_until_line = j
                break
        continue
    
    # 6. Fix closing tags before script
    if '<script>' in line and i > 1000:
        output_lines.append('            </div>\n')  # Close main-content
        output_lines.append('        </div>\n')  # Close main-wrapper
        output_lines.append('    </div>\n')  # Close dashboard-container
        output_lines.append('\n')
        output_lines.append(line)
        skip_until_line = i + 1
        continue
    
    # Default: keep the line
    output_lines.append(line)

# Write the new file
with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("Dashboard reorganization complete!")
print(f"Processed {len(lines)} lines, output {len(output_lines)} lines")
