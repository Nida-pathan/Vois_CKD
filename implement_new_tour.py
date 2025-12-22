# Script: Implement New Tour with Separate Message Box and Pointer
# This completely replaces the driver.js tour with a custom implementation

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the old tour CSS and JS (everything between the tour style and script tags)
# We'll replace it with a completely new implementation

# New Tour CSS - Separate message box and pointer styles
new_tour_css = '''    <!-- Custom Tour Styles -->
    <style>
        /* Fixed Message Box - Always visible in corner */
        .tour-message-box {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 350px;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            z-index: 10001;
            overflow: visible;
            font-family: 'Inter', sans-serif;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .tour-message-content {
            padding: 25px;
        }
        
        .tour-message-title {
            font-size: 20px;
            font-weight: 700;
            color: #0d9488;
            margin: 0 0 10px 0;
        }
        
        .tour-message-description {
            font-size: 14px;
            color: #4b5563;
            line-height: 1.6;
            margin: 0;
        }
        
        .tour-message-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 25px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            border-bottom-left-radius: 16px;
            border-bottom-right-radius: 16px;
        }
        
        .tour-progress {
            color: #94a3b8;
            font-size: 13px;
        }
        
        .tour-buttons button {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            margin-left: 8px;
            transition: all 0.2s;
        }
        
        .tour-btn-back {
            background: white;
            border: 1px solid #e2e8f0;
            color: #475569;
        }
        
        .tour-btn-back:hover {
            background: #f1f5f9;
        }
        
        .tour-btn-next {
            background: #0d9488;
            border: 1px solid #0d9488;
            color: white;
        }
        
        .tour-btn-next:hover {
            background: #0f766e;
        }
        
        .tour-btn-skip {
            background: transparent;
            border: none;
            color: #94a3b8;
            font-size: 12px;
            cursor: pointer;
        }
        
        /* Avatar floating outside message box */
        .tour-avatar {
            position: absolute;
            top: -40px;
            right: 20px;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #ffffff;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            background: #f0fdfa;
        }
        
        /* Separate Pointer/Highlight Box */
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
        }
        
        .tour-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9999;
            pointer-events: none;
        }
    </style>'''

# New Tour JavaScript
new_tour_js = '''    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const shouldShowTour = {{ 'true' if show_tour else 'false' }};
            const alwaysShowUser = 'ar3';
            const currentUser = '{{ current_user.username }}';
            
            if (!shouldShowTour && currentUser !== alwaysShowUser) {
                console.log('Tour logic: Not showing tour.');
                return;
            }

            console.log('Starting Custom Tour...');
            initCustomTour();
        });

        function initCustomTour() {
            const avatarUrl = "{{ url_for('static', filename='images/ai_avatar.png') }}";
            const username = "{{ current_user.username }}";
            
            const steps = [
                {
                    element: '.welcome-message',
                    title: `Welcome, ${username}!`,
                    description: "I'm your AI Health Assistant. Let me show you around your new dashboard."
                },
                {
                    element: '#upload-section',
                    title: 'Lab Analysis',
                    description: "Upload your lab reports here. I'll analyze them instantly to track your kidney health."
                },
                {
                    element: '#chatbot-trigger',
                    title: "I'm Here to Help",
                    description: "Click here anytime to chat with me. I can answer questions about your health, diet, or reports."
                }
            ];
            
            let currentStep = 0;
            
            // Create the message box (fixed position)
            const messageBox = document.createElement('div');
            messageBox.className = 'tour-message-box';
            messageBox.id = 'tour-message-box';
            
            // Create the pointer element
            const pointer = document.createElement('div');
            pointer.className = 'tour-pointer';
            pointer.id = 'tour-pointer';
            
            document.body.appendChild(messageBox);
            document.body.appendChild(pointer);
            
            function showStep(index) {
                const step = steps[index];
                const targetElement = document.querySelector(step.element);
                
                if (!targetElement) {
                    console.error('Target element not found:', step.element);
                    return;
                }
                
                // Update message box content
                messageBox.innerHTML = `
                    <img src="${avatarUrl}" class="tour-avatar" alt="AI Assistant">
                    <div class="tour-message-content">
                        <h3 class="tour-message-title">${step.title}</h3>
                        <p class="tour-message-description">${step.description}</p>
                    </div>
                    <div class="tour-message-footer">
                        <span class="tour-progress">${index + 1} of ${steps.length}</span>
                        <div class="tour-buttons">
                            ${index > 0 ? '<button class="tour-btn-back" onclick="tourBack()">Back</button>' : ''}
                            <button class="tour-btn-next" onclick="tourNext()">
                                ${index === steps.length - 1 ? 'Get Started' : 'Next'}
                            </button>
                        </div>
                    </div>
                    <button class="tour-btn-skip" onclick="tourEnd()">Skip Tour</button>
                `;
                
                // Position the pointer on the target element
                const rect = targetElement.getBoundingClientRect();
                const padding = 10;
                pointer.style.top = (rect.top + window.scrollY - padding) + 'px';
                pointer.style.left = (rect.left + window.scrollX - padding) + 'px';
                pointer.style.width = (rect.width + padding * 2) + 'px';
                pointer.style.height = (rect.height + padding * 2) + 'px';
                
                // Scroll target into view
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Global functions for button clicks
            window.tourNext = function() {
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    showStep(currentStep);
                } else {
                    tourEnd();
                }
            };
            
            window.tourBack = function() {
                if (currentStep > 0) {
                    currentStep--;
                    showStep(currentStep);
                }
            };
            
            window.tourEnd = function() {
                messageBox.remove();
                pointer.remove();
                
                // Mark tour as seen
                fetch('/api/complete-tour', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(response => {
                    if(response.ok) console.log('Tour marked as seen');
                }).catch(err => console.error('Error marking tour:', err));
            };
            
            // Start the tour
            showStep(0);
        }
    </script>'''

# Remove old tour code (from <!-- Driver.js --> or similar to the closing </script> before </body>)
# Find the section with driver.js CDN links and tour code
pattern = r'<!-- Driver\.js Tour Library -->.*?</script>\s*(?=\s*</body>)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Also remove any old tour style blocks
pattern2 = r'<style>\s*/\* Custom Tour Styles \*/.*?</style>\s*<script>.*?function markTourAsSeen\(\).*?</script>'
content = re.sub(pattern2, '', content, flags=re.DOTALL)

# Insert new tour code before </body>
content = content.replace('</body>', new_tour_css + '\n\n' + new_tour_js + '\n</body>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("New Tour Implementation Complete!")
print("")
print("Created 2 SEPARATE elements:")
print("1. MESSAGE BOX - Fixed at bottom-right corner with avatar")
print("2. POINTER - Highlights the target section with pulsing border")
print("")
print("Refresh the page to see the new tour!")
