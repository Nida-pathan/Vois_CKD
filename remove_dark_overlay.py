# Script: Remove dark overlay - keep only the pointer border

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the box-shadow that creates the dark overlay from pointer CSS
# Keep only the glow effect around the border

content = re.sub(
    r'0 0 0 4000px rgba\(0, 0, 0, 0\.3\)',
    '0 0 0 0 transparent',
    content
)

# Also update the pulse animation to not include overlay
old_pulse = '''        @keyframes pulse {
            0%, 100% { 
                box-shadow: 
                    0 0 0 4000px rgba(0, 0, 0, 0.3),
                    0 0 30px rgba(13, 148, 136, 0.8),
                    inset 0 0 20px rgba(13, 148, 136, 0.3);
                border-color: #0d9488;
            }
            50% { 
                box-shadow: 
                    0 0 0 4000px rgba(0, 0, 0, 0.3),
                    0 0 50px rgba(13, 148, 136, 1),
                    inset 0 0 30px rgba(13, 148, 136, 0.5);
                border-color: #14b8a6;
            }
        }'''

new_pulse = '''        @keyframes pulse {
            0%, 100% { 
                box-shadow: 
                    0 0 30px rgba(13, 148, 136, 0.8),
                    inset 0 0 20px rgba(13, 148, 136, 0.3);
                border-color: #0d9488;
            }
            50% { 
                box-shadow: 
                    0 0 50px rgba(13, 148, 136, 1),
                    inset 0 0 30px rgba(13, 148, 136, 0.5);
                border-color: #14b8a6;
            }
        }'''

content = content.replace(old_pulse, new_pulse)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Dark overlay completely removed.")
print("Now the tour shows:")
print("- Glowing teal border around target element")
print("- NO dark overlay on the rest of the page")
print("- Message box in corner")
