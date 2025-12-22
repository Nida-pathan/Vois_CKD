# Script: Disable all other clicks during tour

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add a click-blocking overlay CSS
new_overlay_css = '''
        /* Click-blocking overlay during tour */
        .tour-click-blocker {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9998;
            background: transparent;
            cursor: not-allowed;
        }
'''

# Insert this CSS after the tour-overlay style
content = re.sub(
    r'(\.tour-overlay \{[^}]+\})',
    r'\1' + new_overlay_css,
    content
)

# Update initCustomTour to add the click blocker
old_append = '''            document.body.appendChild(messageBox);
            document.body.appendChild(pointer);'''

new_append = '''            // Add click blocker to disable all other clicks during tour
            const clickBlocker = document.createElement('div');
            clickBlocker.className = 'tour-click-blocker';
            clickBlocker.id = 'tour-click-blocker';
            document.body.appendChild(clickBlocker);
            
            document.body.appendChild(messageBox);
            document.body.appendChild(pointer);'''

content = content.replace(old_append, new_append)

# Update tourEnd to remove the click blocker
old_cleanup = '''                // Remove ALL tour-related elements
                document.querySelectorAll('.tour-message-box, .tour-pointer, .tour-overlay').forEach(el => el.remove());'''

new_cleanup = '''                // Remove ALL tour-related elements including click blocker
                document.querySelectorAll('.tour-message-box, .tour-pointer, .tour-overlay, .tour-click-blocker').forEach(el => el.remove());
                const blocker = document.getElementById('tour-click-blocker');
                if (blocker) blocker.remove();'''

content = content.replace(old_cleanup, new_cleanup)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Click blocking enabled during tour:")
print("- Transparent overlay blocks all page clicks")
print("- Only tour buttons (Next, Back, Skip) are clickable")
print("- Overlay removed when tour ends")
