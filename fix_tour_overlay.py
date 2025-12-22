# Script: Fix the tour overlay - make background visible

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the dark overlay (0.7) with a lighter one (0.3)
content = content.replace('0 0 0 4000px rgba(0, 0, 0, 0.7)', '0 0 0 4000px rgba(0, 0, 0, 0.3)')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed! Reduced overlay opacity from 0.7 to 0.3")
print("Background should now be visible!")
