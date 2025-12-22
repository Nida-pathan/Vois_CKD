# Script 1: Fix Jinja Template Syntax
# This script fixes the broken {{ }} syntax in the tour code

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken Jinja syntax where {{ }} is split across lines
pattern = r"const shouldShowTour = \{\{ 'true' if show_tour else 'false' \}\s*\r?\n\s*\};"
replacement = "const shouldShowTour = {{ 'true' if show_tour else 'false' }};"

content = re.sub(pattern, replacement, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Script 1 Complete: Fixed Jinja template syntax")
