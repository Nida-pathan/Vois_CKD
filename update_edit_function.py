# Script to update the editPatient function in doctor_dashboard.html
with open('templates/doctor_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the editPatient function
old_function = """    // Edit patient
    function editPatient(patientId) {
        // In a real implementation, this would open an edit form
        alert(`Edit functionality for patient ${patientId} would be implemented here.`);
    }"""

new_function = """    // View patient details
    function viewPatientDetails(patientId) {
        window.location.href = `/results/${patientId}`;
    }

    // Edit patient - redirects to results page (same as view for now)
    function editPatient(patientId) {
        window.location.href = `/results/${patientId}`;
    }"""

# Replace the old function
if old_function in content:
    content = content.replace(old_function, new_function)
    
    with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Successfully updated editPatient function")
else:
    print("Could not find the editPatient function to replace")
    # Try to find just the edit function
    if "function editPatient" in content:
        print("Found editPatient function but pattern doesn't match exactly")
