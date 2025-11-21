#!/usr/bin/env python3
"""
Script to reorganize the doctor dashboard layout:
1. Move menu to left sidebar
2. Move doctor name below top bar
3. Move action buttons to profile card
"""

# Read the original file
with open('templates/doctor_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Update CSS for flexbox layout with left sidebar
old_container_css = """        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
        }"""

new_container_css = """        .dashboard-container {
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

content = content.replace(old_container_css, new_container_css)

# Step 2: Update dashboard-grid to remove right sidebar column
old_grid_css = """        /* Main Content Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 3fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }"""

new_grid_css = """        /* Main Content Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }"""

content = content.replace(old_grid_css, new_grid_css)

# Step 3: Restructure HTML body - create left sidebar with menu
# Find the body tag and restructure
old_body_start = """<body>
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
        </div>"""

new_body_start = """<body>
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
            <input type="file" id="pdfUpload" accept=".pdf" style="display: none;" onchange="uploadPDF(this)">"""

content = content.replace(old_body_start, new_body_start)

# Step 4: Update profile card to include action buttons
old_profile_card = """                <!-- Profile Card -->
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

new_profile_card = """                <!-- Profile Card with Action Buttons -->
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

content = content.replace(old_profile_card, new_profile_card)

# Step 5: Remove the right sidebar (menu section)
# Find and remove the sidebar section
import re
sidebar_pattern = r'            <!-- Right Sidebar -->.*?            <!-- Skills Card -->.*?</div>\s*</div>'
content = re.sub(sidebar_pattern, '', content, flags=re.DOTALL)

# Step 6: Fix closing tags - add closing divs for main-wrapper
old_closing = """        </div>
    </div>

    <script>"""

new_closing = """            </div>
        </div>
    </div>

    <script>"""

content = content.replace(old_closing, new_closing)

# Write the modified content
with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard reorganization complete!")
