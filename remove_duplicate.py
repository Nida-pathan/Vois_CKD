# Script to remove duplicate viewPatientDetails function
with open('templates/doctor_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove the duplicate viewPatientDetails function (lines 758-761)
# We'll keep only one instance
new_lines = []
skip_next = 0
found_first_view = False

for i, line in enumerate(lines):
    if skip_next > 0:
        skip_next -= 1
        continue
    
    # Check if this is a duplicate viewPatientDetails function
    if 'function viewPatientDetails(patientId)' in line and found_first_view:
        # Skip this function and the next 3 lines (the function body)
        skip_next = 3
        continue
    
    if 'function viewPatientDetails(patientId)' in line:
        found_first_view = True
    
    new_lines.append(line)

with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully removed duplicate viewPatientDetails function")
