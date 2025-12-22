# Script 2: Fix Tour Overlap Issue
# This script fixes the CSS to prevent overlap while keeping popover on screen

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Reduce margin-top to 40px - balanced value to prevent overlap but stay on screen
content = re.sub(
    r"\.driver-popover\.tour-theme\s*\{\s*\n\s*margin-top:\s*\d+px\s*!important;",
    ".driver-popover.tour-theme {\n            margin-top: 40px !important;",
    content
)

content = re.sub(
    r"\.driver-popover\s*\{\s*\n\s*margin-top:\s*\d+px\s*!important;",
    ".driver-popover {\n            margin-top: 40px !important;",
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Script 2 Complete: Reduced margin-top to 40px (balanced value)")
