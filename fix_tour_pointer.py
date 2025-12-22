# Script: Make the tour pointer more visible

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the pointer CSS to make it more visible
old_pointer_css = '''        /* Separate Pointer/Highlight Box */
        .tour-pointer {
            position: absolute;
            border: 3px solid #0d9488;
            border-radius: 12px;
            z-index: 10000;
            pointer-events: none;
            box-shadow: 0 0 0 4000px rgba(0, 0, 0, 0.5);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 4000px rgba(0, 0, 0, 0.5), 0 0 0 0 rgba(13, 148, 136, 0.4); }
            50% { box-shadow: 0 0 0 4000px rgba(0, 0, 0, 0.5), 0 0 0 10px rgba(13, 148, 136, 0); }
        }'''

new_pointer_css = '''        /* Separate Pointer/Highlight Box - MORE VISIBLE */
        .tour-pointer {
            position: absolute;
            border: 5px solid #0d9488;
            border-radius: 12px;
            z-index: 10000;
            pointer-events: none;
            background: rgba(13, 148, 136, 0.1);
            box-shadow: 
                0 0 0 4000px rgba(0, 0, 0, 0.7),
                0 0 30px rgba(13, 148, 136, 0.8),
                inset 0 0 20px rgba(13, 148, 136, 0.3);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { 
                box-shadow: 
                    0 0 0 4000px rgba(0, 0, 0, 0.7),
                    0 0 30px rgba(13, 148, 136, 0.8),
                    inset 0 0 20px rgba(13, 148, 136, 0.3);
                border-color: #0d9488;
            }
            50% { 
                box-shadow: 
                    0 0 0 4000px rgba(0, 0, 0, 0.7),
                    0 0 50px rgba(13, 148, 136, 1),
                    inset 0 0 30px rgba(13, 148, 136, 0.5);
                border-color: #14b8a6;
            }
        }'''

content = content.replace(old_pointer_css, new_pointer_css)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Pointer visibility enhanced!")
print("Changes:")
print("- Thicker border (5px instead of 3px)")
print("- Added glow effect (30-50px glow)")
print("- Added inner glow")
print("- Darker overlay (0.7 instead of 0.5)")
print("- Faster pulse animation (1.5s)")
print("")
print("Refresh the page!")
