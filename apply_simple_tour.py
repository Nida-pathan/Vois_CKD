# Script: Replace custom tour with simpler driver.js tour from user's provided HTML

import re

filepath = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the custom tour CSS (from <!-- Custom Tour Styles --> to just before the tour script)
content = re.sub(
    r'<!-- Custom Tour Styles -->.*?</style>\s*<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function \(\) \{.*?function initCustomTour\(\).*?</script>',
    '''<!-- Tour using Driver.js -->
    <script>
        // Tour Logic
        document.addEventListener('DOMContentLoaded', function () {
            // Check if we should show the tour
            const showTour = {{ 'true' if show_tour else 'false' }};

            console.log('Tour check - showTour:', showTour);

            if (showTour) {
                console.log('Initializing tour...');

                // Wait for driver.js to load
                setTimeout(() => {
                    if (!window.driver || !window.driver.js) {
                        console.error('Driver.js not loaded!');
                        return;
                    }

                    // Initialize driver
                    const driver = window.driver.js.driver;
                    const avatarUrl = "{{ url_for('static', filename='images/ai_avatar.png') }}";

                    const driverObj = driver({
                        showProgress: true,
                        animate: true,
                        allowClose: true,
                        overlayColor: 'rgba(0, 0, 0, 0.6)',
                        popoverClass: 'tour-popover',
                        onDestroyStarted: () => {
                            // Mark tour as complete when finished or closed
                            fetch('/api/complete-tour', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' }
                            }).then(() => console.log('Tour marked complete'));
                            driverObj.destroy();
                        },
                        steps: [
                            {
                                element: '.welcome-message',
                                popover: {
                                    title: 'Welcome!',
                                    description: "Hi! I'm your Personal Health Assistant. I'll quickly show you around your dashboard.",
                                    side: "bottom",
                                    align: 'start'
                                }
                            },
                            {
                                element: '#stats-overview',
                                popover: {
                                    title: 'Health Overview',
                                    description: 'See your key metrics like CKD Stage and Risk Level at a glance right here.',
                                    side: "bottom",
                                    align: 'start'
                                }
                            },
                            {
                                element: '#upload-section',
                                popover: {
                                    title: 'Analysis Tool',
                                    description: "Upload your lab reports here. I'll analyze them to track your progress automatically.",
                                    side: "top",
                                    align: 'start'
                                }
                            },
                            {
                                element: '#chatbot-trigger',
                                popover: {
                                    title: 'Chat with Me',
                                    description: "I'm always here! Click this button to ask me anything about your health.",
                                    side: "left",
                                    align: 'start'
                                }
                            }
                        ]
                    });

                    // Custom styling for the popover
                    const style = document.createElement('style');
                    style.innerHTML = `
                        .tour-popover {
                            max-width: 400px !important;
                            border-radius: 16px !important;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
                        }
                        .driver-popover-title {
                            font-size: 18px !important;
                            font-weight: 700 !important;
                            color: #0d9488 !important;
                            margin-bottom: 8px !important;
                        }
                        .driver-popover-description {
                            font-size: 14px !important;
                            color: #4b5563 !important;
                            line-height: 1.5 !important;
                        }
                    `;
                    document.head.appendChild(style);

                    // Start tour after a short delay
                    setTimeout(() => {
                        console.log('Starting tour...');
                        driverObj.drive();
                    }, 1000);
                }, 500);
            } else {
                console.log('Tour already seen or not applicable');
            }
        });
    </script>''',
    content,
    flags=re.DOTALL
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced custom tour with simpler driver.js tour!")
print("- Uses built-in driver.js styling")
print("- No click blocker needed")
print("- Chatbot will work during and after tour")
