# Script: Ensure NO opacity remains after tour ends

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the tourEnd function and ensure it removes ALL overlays/opacity
old_tourEnd = '''            window.tourEnd = function() {
                // Remove all tour elements completely
                const msgBox = document.getElementById('tour-message-box');
                const ptr = document.getElementById('tour-pointer');
                
                if (msgBox) msgBox.remove();
                if (ptr) ptr.remove();
                
                // Also remove any leftover tour elements by class
                document.querySelectorAll('.tour-message-box, .tour-pointer, .tour-overlay').forEach(el => el.remove());
                
                // Remove any inline styles that might have been added
                document.body.style.overflow = '';
                
                // Mark tour as seen
                fetch('/api/complete-tour', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(response => {
                    if(response.ok) console.log('Tour completed and marked as seen');
                }).catch(err => console.error('Error marking tour:', err));
                
                console.log('Tour ended - screen restored to normal');
            };'''

new_tourEnd = '''            window.tourEnd = function() {
                // Remove all tour elements completely - NO OPACITY LEFT
                const msgBox = document.getElementById('tour-message-box');
                const ptr = document.getElementById('tour-pointer');
                
                if (msgBox) msgBox.remove();
                if (ptr) ptr.remove();
                
                // Remove ALL tour-related elements
                document.querySelectorAll('.tour-message-box, .tour-pointer, .tour-overlay').forEach(el => el.remove());
                
                // Reset body styles completely
                document.body.style.overflow = '';
                document.body.style.opacity = '1';
                document.body.style.filter = '';
                
                // Remove any dynamically added style elements for tour
                document.querySelectorAll('style[data-tour]').forEach(el => el.remove());
                
                // Force repaint to clear any visual artifacts
                document.body.offsetHeight;
                
                // Mark tour as seen
                fetch('/api/complete-tour', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(response => {
                    if(response.ok) console.log('Tour completed and marked as seen');
                }).catch(err => console.error('Error marking tour:', err));
                
                console.log('Tour ended - screen fully restored, no opacity');
            };'''

content = content.replace(old_tourEnd, new_tourEnd)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Tour cleanup now ensures:")
print("- Body opacity reset to 1 (100%)")
print("- Body filter reset")
print("- All tour elements removed")
print("- Force repaint to clear artifacts")
print("")
print("After tour ends = COMPLETELY CLEAR SCREEN")
