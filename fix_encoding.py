
try:
    with open('templates/doctor_dashboard.html', 'r', encoding='utf-16') as f:
        content = f.read()
except UnicodeError:
    # Try utf-8 just in case
    with open('templates/doctor_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
