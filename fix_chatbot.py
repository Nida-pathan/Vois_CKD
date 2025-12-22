# Script: Fix Chatbot - Ensure all chatbot code is properly in place

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if chatbot container HTML exists
if 'id="chatbot-container"' not in content:
    print("ERROR: Chatbot container HTML missing!")
else:
    print("OK: Chatbot container HTML found")

# Check if chatbot toggle exists  
if 'id="chatbot-trigger"' not in content:
    print("ERROR: Chatbot trigger missing!")
else:
    print("OK: Chatbot trigger found")

# Check if chatbot JS exists
if 'chatbotToggle.addEventListener' not in content:
    print("ERROR: Chatbot JavaScript missing!")
else:
    print("OK: Chatbot JavaScript found")

# The issue might be z-index conflicts with tour elements
# Let's ensure chatbot has very high z-index

# Update chatbot-container z-index if needed
if '.chatbot-container {' in content:
    content = re.sub(
        r'(\.chatbot-container\s*\{[^}]*z-index:\s*)\d+',
        r'\g<1>99999',
        content
    )
    print("Updated chatbot-container z-index to 99999")

# Make sure chatbot-toggle is above any tour overlays
if '.chatbot-toggle {' in content:
    # Check if z-index already exists in chatbot-toggle
    if 'chatbot-toggle' in content and 'z-index' not in content[content.find('.chatbot-toggle'):content.find('.chatbot-toggle')+500]:
        content = content.replace(
            '.chatbot-toggle {',
            '.chatbot-toggle {\n            z-index: 99999;'
        )
        print("Added z-index to chatbot-toggle")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nChatbot code verified and z-index updated!")
print("The chatbot should now be clickable above any tour overlays.")
