#!/usr/bin/env python3
"""
Fixed version: Reorganize dashboard with careful preservation of Jinja2 templates
"""

with open('templates/doctor_dashboard_backup.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS: Update dashboard-container
content = content.replace(
    """        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
        }""",
    """        .dashboard-container {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            gap: 20px;
        }

        /* Left Sidebar */
        .left-sidebar {
            width: 250px;
            flex-shrink: 0;
        }

        .main-wrapper {
            flex: 1;
            min-width: 0;
        }"""
)

# 2. CSS: Update dashboard-grid
content = content.replace(
    """        /* Main Content Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 3fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }""",
    """        /* Main Content Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }"""
)

# 3. HTML: Replace body opening through stats grid
old_body_section = """<body>
    <div class="dashboard-container">
        <!-- Top Welcome Section -->
        <div class="top-bar">
            <div class="logo">
                <div class="logo-icon">
                    <i class="fas fa-heartbeat"></i>
                </div>
                <span>CKD Diagnostic System</span>
            </div>

            <div class="welcome-text">Welcome, <span>Dr. {{ current_user.username }}</span></div>

            <div class="top-bar-right">
                <div class="actions-group" style="display: flex; gap: 15px; align-items: center; margin-right: 20px;">
                    <button onclick="window.location.href='{{ url_for('add_patient') }}'" class="btn-action">
                        <i class="fas fa-user-plus"></i> Add Patient
                    </button>

                    <button onclick="document.getElementById('pdfUpload').click()" class="btn-action">
                        <i class="fas fa-file-upload"></i> Upload Prescription
                    </button>

                    <!-- Hidden inputs for file upload -->
                    <input type="file" id="pdfUpload" accept=".pdf" style="display: none;" onchange="uploadPDF(this)">
                </div>

                <div class="search-bar">
                    <i class="fas fa-search"></i>
                    <input type="text" id="patientSearch" placeholder="Search patients..." onkeyup="filterPatients()">
                </div>

                <div class="top-icon-btn" onclick="toggleTheme()" title="Toggle Dark Mode">
                    <i class="fas fa-moon" id="themeIcon"></i>
                </div>

                <div class="top-icon-btn" title="Notifications">
                    <i class="fas fa-bell"></i>
                    <span class="notification-badge"></span>
                </div>

                <div class="profile-icon" onclick="window.location.href='{{ url_for('logout') }}'" title="Logout">
                    <i class="fas fa-sign-out-alt"></i>
                </div>
            </div>
        </div>

        <!-- Stats Grid -->"""

new_body_section = """<body>
    <div class="dashboard-container">
        <!-- Left Sidebar with Menu -->
        <div class="left-sidebar">
            <div class="nav-card">
                <div class="sidebar-title">Menu</div>
                <div class="nav-list">
                    <a href="{{ url_for('doctor_dashboard') }}" class="nav-item active">
                        <i class="fas fa-th-large"></i>
                        <span>Dashboard</span>
                    </a>
                    <a href="{{ url_for('appointments') }}" class="nav-item">
                        <i class="fas fa-calendar-alt"></i>
                        <span>Appointments</span>
                    </a>
                    <a href="{{ url_for('messages') }}" class="nav-item">
                        <i class="fas fa-comments"></i>
                        <span>Messages</span>
                    </a>
                    <a href="{{ url_for('prescriptions') }}" class="nav-item">
                        <i class="fas fa-file-prescription"></i>
                        <span>Prescriptions</span>
                    </a>
                    <a href="{{ url_for('lab_results') }}" class="nav-item">
                        <i class="fas fa-flask"></i>
                        <span>Lab Results</span>
                    </a>
                    <a href="{{ url_for('education') }}" class="nav-item">
                        <i class="fas fa-book-medical"></i>
                        <span>Education</span>
                    </a>
                </div>
            </div>
        </div>

        <!-- Main Content Wrapper -->
        <div class="main-wrapper">
            <!-- Top Bar -->
            <div class="top-bar">
                <div class="logo">
                    <div class="logo-icon">
                        <i class="fas fa-heartbeat"></i>
                    </div>
                    <span>CKD Diagnostic System</span>
                </div>

                <div class="top-bar-right">
                    <div class="search-bar">
                        <i class="fas fa-search"></i>
                        <input type="text" id="patientSearch" placeholder="Search patients..." onkeyup="filterPatients()">
                    </div>

                    <div class="top-icon-btn" onclick="toggleTheme()" title="Toggle Dark Mode">
                        <i class="fas fa-moon" id="themeIcon"></i>
                    </div>

                    <div class="top-icon-btn" title="Notifications">
                        <i class="fas fa-bell"></i>
                        <span class="notification-badge"></span>
                    </div>

                    <div class="profile-icon" onclick="window.location.href='{{ url_for('logout') }}'" title="Logout">
                        <i class="fas fa-sign-out-alt"></i>
                    </div>
                </div>
            </div>

            <!-- Doctor Name Bar -->
            <div class="welcome-text" style="background: var(--glass-bg); padding: 15px 20px; border-radius: var(--border-radius-md); margin-bottom: 20px; margin-top: 20px; border: 1px solid var(--glass-border); backdrop-filter: blur(10px); box-shadow: var(--shadow-light);">
                Welcome, <span>Dr. {{ current_user.username }}</span>
            </div>

            <!-- Hidden input for file upload -->
            <input type="file" id="pdfUpload" accept=".pdf" style="display: none;" onchange="uploadPDF(this)">

            <!-- Stats Grid -->"""

content = content.replace(old_body_section, new_body_section)

# 4. HTML: Update profile card to add action buttons
old_profile = """                <!-- Profile Card -->
                <div class="profile-card">
                    <div class="profile-header">
                        <div class="profile-photo">{{ current_user.username[:2].upper() }}</div>
                        <div class="profile-info">
                            <h2>Dr. {{ current_user.username }}</h2>
                            <p>{{ current_user.specialization if current_user.specialization else 'Nephrologist' }}</p>
                            <div class="stats-pills">
                                <div class="stat-pill">
                                    <i class="fas fa-users"></i>
                                    <span>{{ patients|length }} patients</span>
                                </div>
                                <div class="stat-pill">
                                    <i class="fas fa-file-medical"></i>
                                    <span>{{ patients|length }} reports</span>
                                </div>
                                <div class="stat-pill">
                                    <i class="fas fa-award"></i>
                                    <span>Experienced</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""

new_profile = """                <!-- Profile Card with Action Buttons -->
                <div class="profile-card">
                    <div class="profile-header">
                        <div class="profile-photo">{{ current_user.username[:2].upper() }}</div>
                        <div class="profile-info">
                            <h2>Dr. {{ current_user.username }}</h2>
                            <p>{{ current_user.specialization if current_user.specialization else 'Nephrologist' }}</p>
                            <div class="stats-pills">
                                <div class="stat-pill">
                                    <i class="fas fa-users"></i>
                                    <span>{{ patients|length }} patients</span>
                                </div>
                                <div class="stat-pill">
                                    <i class="fas fa-file-medical"></i>
                                    <span>{{ patients|length }} reports</span>
                                </div>
                                <div class="stat-pill">
                                    <i class="fas fa-award"></i>
                                    <span>Experienced</span>
                                </div>
                            </div>
                        </div>
                        <div class="actions-group" style="display: flex; gap: 10px; margin-left: auto;">
                            <button onclick="window.location.href='{{ url_for('add_patient') }}'" class="btn-action">
                                <i class="fas fa-user-plus"></i> Add Patient
                            </button>
                            <button onclick="document.getElementById('pdfUpload').click()" class="btn-action">
                                <i class="fas fa-file-upload"></i> Upload Prescription
                            </button>
                        </div>
                    </div>
                </div>"""

content = content.replace(old_profile, new_profile)

# 5. HTML: Remove right sidebar - find it precisely
import re
# Find the sidebar section - it starts with "<!-- Right Sidebar -->" and ends before the closing dashboard-grid div
sidebar_start = content.find('            <!-- Right Sidebar -->')
if sidebar_start != -1:
    # Find the end - look for the closing </div> of the sidebar
    # The sidebar has 3 cards, so we need to find where it ends
    temp_pos = sidebar_start
    div_count = 0
    sidebar_end = -1
    
    # Skip to the opening <div class="sidebar">
    temp_pos = content.find('<div class="sidebar">', sidebar_start)
    if temp_pos != -1:
        temp_pos += len('<div class="sidebar">')
        div_count = 1
        
        # Count divs to find the matching closing tag
        while temp_pos < len(content) and div_count > 0:
            next_open = content.find('<div', temp_pos)
            next_close = content.find('</div>', temp_pos)
            
            if next_close == -1:
                break
                
            if next_open != -1 and next_open < next_close:
                div_count += 1
                temp_pos = next_open + 4
            else:
                div_count -= 1
                if div_count == 0:
                    sidebar_end = next_close + 6
                    break
                temp_pos = next_close + 6
        
        if sidebar_end != -1:
            # Remove the sidebar section
            content = content[:sidebar_start] + content[sidebar_end:]

# 6. Fix closing tags before script
content = content.replace(
    """        </div>
    </div>

    <script>""",
    """            </div>
        </div>
    </div>

    <script>"""
)

# Write the result
with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard reorganization complete (v3 - fixed)!")
print(f"Output length: {len(content)} characters")

# Verify Jinja2 templates are present
if '{% for patient in patients %}' in content:
    print("✓ Patient loop preserved")
else:
    print("✗ WARNING: Patient loop missing!")

if '{% for i in range(1, 6) %}' in content:
    print("✓ Range loop preserved")
else:
    print("✗ WARNING: Range loop missing!")
