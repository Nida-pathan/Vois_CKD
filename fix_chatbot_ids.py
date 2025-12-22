# Script: Fix chatbot by adding missing ID and ensuring proper element selection

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add id to chatbot-container that's missing it
content = content.replace(
    '<div class="chatbot-container">',
    '<div id="chatbot-container" class="chatbot-container">'
)

# Fix 2: Add id to chatbot-window if missing
content = content.replace(
    '<div class="chatbot-window">',
    '<div id="chatbot-window" class="chatbot-window">'
)

# Fix 3: Add id to chatbot-close if missing
content = content.replace(
    '<button class="chatbot-close">',
    '<button id="chatbot-close" class="chatbot-close">'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed chatbot HTML!")
print("- Added id='chatbot-container' to .chatbot-container")
print("- Added id='chatbot-window' to .chatbot-window")
print("- Added id='chatbot-close' to .chatbot-close")
print("")
print("Chatbot should now open on click!")
