# Script: Remove duplicate chatbot container

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Count how many chatbot containers exist
matches = re.findall(r'<div[^>]*class="chatbot-container"[^>]*>', content)
print(f"Found {len(matches)} chatbot containers")

# Remove the first/older chatbot (line 1355-1375 area) that doesn't have proper IDs
# This is the one with fa-comment-medical icon
old_chatbot = '''    <!-- Patient Education Chatbot -->
    <div id="chatbot-container" class="chatbot-container">
        <div class="chatbot-toggle" id="chatbot-trigger">
            <i class="fas fa-comment-medical"></i>
        </div>
        <div id="chatbot-window" class="chatbot-window">
            <div class="chatbot-header">
                <h3><i class="fas fa-robot"></i> Health Assistant</h3>
                <button id="chatbot-close" class="chatbot-close">&times;</button>
            </div>
            <div class="chatbot-messages" id="chatbot-messages">
                <div class="chatbot-message bot">
                    <div class="chatbot-message-content">Loading assistant...</div>
                </div>
            </div>
            <div class="chatbot-input-container">
                <input type="text" class="chatbot-input" id="chatbot-input" placeholder="Ask me about your health..." />
                <button class="chatbot-send" id="chatbot-send">Send</button>
            </div>
        </div>
    </div>'''

if old_chatbot in content:
    content = content.replace(old_chatbot, '')
    print("Removed first duplicate chatbot (with fa-comment-medical icon)")
else:
    print("Could not find exact match for first chatbot, trying alternate pattern...")
    # Try pattern matching
    content = re.sub(
        r'<!-- Patient Education Chatbot -->\s*<div[^>]*chatbot-container[^>]*>.*?<i class="fas fa-comment-medical"></i>.*?</div>\s*</div>\s*</div>\s*</div>\s*</div>',
        '',
        content,
        flags=re.DOTALL,
        count=1
    )
    print("Removed duplicate chatbot using pattern")

# Count again
matches = re.findall(r'<div[^>]*class="chatbot-container"[^>]*>', content)
print(f"Now have {len(matches)} chatbot container(s)")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone! Duplicate chatbot removed.")
