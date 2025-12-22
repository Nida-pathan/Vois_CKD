# Script: Fix chatbot click - ensure click blocker is completely removed

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace tourEnd function with more aggressive cleanup
old_tourEnd = '''            window.tourEnd = function () {
                // Remove all tour elements completely - NO OPACITY LEFT
                const msgBox = document.getElementById('tour-message-box');
                const ptr = document.getElementById('tour-pointer');

                if (msgBox) msgBox.remove();
                if (ptr) ptr.remove();

                // Remove ALL tour-related elements including click blocker
                document.querySelectorAll('.tour-message-box, .tour-pointer, .tour-overlay, .tour-click-blocker').forEach(el => el.remove());
                const blocker = document.getElementById('tour-click-blocker');
                if (blocker) blocker.remove();

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
                    if (response.ok) console.log('Tour completed and marked as seen');
                }).catch(err => console.error('Error marking tour:', err));

                console.log('Tour ended - screen fully restored, no opacity');
            };'''

new_tourEnd = '''            window.tourEnd = function () {
                console.log('Tour ending - removing all elements...');
                
                // Remove by ID first
                ['tour-message-box', 'tour-pointer', 'tour-click-blocker'].forEach(id => {
                    const el = document.getElementById(id);
                    if (el) {
                        el.remove();
                        console.log('Removed:', id);
                    }
                });
                
                // Remove by class (backup)
                document.querySelectorAll('.tour-message-box, .tour-pointer, .tour-overlay, .tour-click-blocker').forEach(el => {
                    el.remove();
                });
                
                // Reset body styles
                document.body.style.overflow = '';
                document.body.style.opacity = '1';
                document.body.style.filter = '';
                document.body.style.pointerEvents = '';
                
                // Re-enable all clicks on the page
                document.body.style.pointerEvents = 'auto';
                
                // Force repaint
                document.body.offsetHeight;
                
                // Mark tour as seen
                fetch('/api/complete-tour', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(response => {
                    if (response.ok) console.log('Tour completed and marked as seen');
                }).catch(err => console.error('Error marking tour:', err));
                
                console.log('Tour ended - all clicks should work now');
            };'''

content = content.replace(old_tourEnd, new_tourEnd)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed! Tour cleanup improved:")
print("- Removes click blocker by ID")
print("- Re-enables pointer events on body")
print("- Chatbot should now be clickable after tour ends")
