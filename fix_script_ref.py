# Script to remove the dashboard_refresh.js script tag
with open('templates/doctor_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove the line with dashboard_refresh.js
new_lines = []
for line in lines:
    if 'dashboard_refresh.js' not in line:
        new_lines.append(line)

with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully removed dashboard_refresh.js reference")
