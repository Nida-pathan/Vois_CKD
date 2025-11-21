"""
Script to add dynamic dashboard update JavaScript to doctor_dashboard.html
"""

# Read the current file
with open('templates/doctor_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# JavaScript code to add
js_code = '''
    <!-- Dynamic Dashboard Update Script -->
    <script>
        // Configuration
        const REFRESH_INTERVAL = 30000; // 30 seconds
        let refreshTimer = null;
        let lastUpdateTime = new Date();

        // Helper function to format numbers with animation
        function animateValue(element, start, end, duration = 500) {
            const range = end - start;
            const increment = range / (duration / 16);
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                    current = end;
                    clearInterval(timer);
                }
                
                if (element.textContent.includes('%')) {
                    element.textContent = current.toFixed(1) + '%';
                } else {
                    element.textContent = Math.round(current);
                }
            }, 16);
        }

        // Update statistics cards with animation
        function updateStats() {
            fetch('/api/doctor/dashboard/stats')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to fetch stats');
                    return response.json();
                })
                .then(data => {
                    // Get all stat cards
                    const statCards = document.querySelectorAll('.stat-card');
                    
                    // Update each stat with animation
                    statCards.forEach(card => {
                        const title = card.querySelector('h3').textContent.trim();
                        const numberElement = card.querySelector('.stat-number');
                        const currentValue = parseFloat(numberElement.textContent.replace('%', '')) || 0;
                        
                        // Add updating class for visual feedback
                        card.classList.add('updating');
                        
                        setTimeout(() => {
                            if (title === 'Total Patients') {
                                animateValue(numberElement, currentValue, data.total_patients);
                            } else if (title === 'High Risk Patients') {
                                animateValue(numberElement, currentValue, data.high_risk);
                            } else if (title === 'Stage 5 CKD') {
                                animateValue(numberElement, currentValue, data.stage_5);
                            } else if (title === 'Avg Risk %') {
                                animateValue(numberElement, currentValue, data.avg_risk);
                            }
                            
                            card.classList.remove('updating');
                        }, 100);
                    });
                    
                    lastUpdateTime = new Date();
                    updateLastUpdatedTime();
                })
                .catch(error => {
                    console.error('Error updating stats:', error);
                });
        }

        // Create patient table row HTML
        function createPatientRow(patient) {
            const riskClass = patient.risk_level.toLowerCase().replace(' ', '-');
            return `
                <tr class="fade-in" data-name="${patient.name.toLowerCase()}" data-id="${patient.patient_id.toLowerCase()}">
                    <td>${patient.patient_id}</td>
                    <td>${patient.name}</td>
                    <td>${patient.age}</td>
                    <td>
                        <span class="badge badge-${riskClass}">
                            ${patient.risk_level}
                        </span>
                    </td>
                    <td>${patient.risk_percentage}%</td>
                    <td>Stage ${patient.stage}</td>
                    <td>
                        <button class="btn-sm" onclick="window.location.href='/results/${patient.patient_id}'">View</button>
                    </td>
                </tr>
            `;
        }

        // Update patient table
        function updatePatientTable() {
            fetch('/api/doctor/dashboard/patients')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to fetch patients');
                    return response.json();
                })
                .then(data => {
                    const tbody = document.querySelector('.patients-table tbody');
                    if (!tbody) return;
                    
                    // Add fade-out effect
                    tbody.style.opacity = '0.5';
                    
                    setTimeout(() => {
                        if (data.patients && data.patients.length > 0) {
                            tbody.innerHTML = data.patients.map(p => createPatientRow(p)).join('');
                        } else {
                            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">No patients found</td></tr>';
                        }
                        
                        // Fade back in
                        tbody.style.opacity = '1';
                        
                        lastUpdateTime = new Date();
                        updateLastUpdatedTime();
                    }, 200);
                })
                .catch(error => {
                    console.error('Error updating patient table:', error);
                    const tbody = document.querySelector('.patients-table tbody');
                    if (tbody) tbody.style.opacity = '1';
                });
        }

        // Update "last updated" timestamp
        function updateLastUpdatedTime() {
            const timeElement = document.getElementById('last-updated-time');
            if (timeElement) {
                const now = new Date();
                const seconds = Math.floor((now - lastUpdateTime) / 1000);
                
                if (seconds < 60) {
                    timeElement.textContent = 'Just now';
                } else if (seconds < 3600) {
                    const minutes = Math.floor(seconds / 60);
                    timeElement.textContent = `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
                } else {
                    timeElement.textContent = lastUpdateTime.toLocaleTimeString();
                }
            }
        }

        // Refresh all dashboard data
        function refreshDashboard() {
            const refreshBtn = document.getElementById('refresh-btn');
            if (refreshBtn) {
                refreshBtn.classList.add('spinning');
                refreshBtn.disabled = true;
            }
            
            updateStats();
            updatePatientTable();
            
            setTimeout(() => {
                if (refreshBtn) {
                    refreshBtn.classList.remove('spinning');
                    refreshBtn.disabled = false;
                }
            }, 1000);
        }

        // Start auto-refresh
        function startAutoRefresh() {
            // Clear any existing timer
            if (refreshTimer) {
                clearInterval(refreshTimer);
            }
            
            // Set up new timer
            refreshTimer = setInterval(() => {
                // Only refresh if page is visible
                if (!document.hidden) {
                    updateStats();
                    updatePatientTable();
                }
            }, REFRESH_INTERVAL);
        }

        // Stop auto-refresh
        function stopAutoRefresh() {
            if (refreshTimer) {
                clearInterval(refreshTimer);
                refreshTimer = null;
            }
        }

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopAutoRefresh();
            } else {
                // Refresh immediately when page becomes visible
                refreshDashboard();
                startAutoRefresh();
            }
        });

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            // Add last updated indicator
            const statsGrid = document.querySelector('.stats-grid');
            if (statsGrid) {
                const lastUpdatedDiv = document.createElement('div');
                lastUpdatedDiv.className = 'last-updated';
                lastUpdatedDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
                        <span style="font-size: 0.85rem; color: var(--text-secondary);">
                            <i class="fas fa-clock"></i> Last updated: <span id="last-updated-time">Just now</span>
                        </span>
                        <button id="refresh-btn" onclick="refreshDashboard()" class="refresh-btn" title="Refresh dashboard">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                `;
                statsGrid.parentNode.insertBefore(lastUpdatedDiv, statsGrid.nextSibling);
            }
            
            // Start auto-refresh
            startAutoRefresh();
            
            // Update "last updated" time every 10 seconds
            setInterval(updateLastUpdatedTime, 10000);
            
            console.log('Dashboard auto-refresh initialized (30s interval)');
        });

        // Clean up on page unload
        window.addEventListener('beforeunload', () => {
            stopAutoRefresh();
        });
    </script>

    <style>
        /* Animation for updating stats */
        .stat-card.updating {
            animation: pulse 0.5s ease-in-out;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.02); opacity: 0.9; }
        }

        /* Fade in animation for table rows */
        .fade-in {
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Refresh button styles */
        .refresh-btn {
            background: var(--primary-gradient);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
        }

        .refresh-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .refresh-btn.spinning i {
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* Last updated indicator */
        .last-updated {
            margin-bottom: 20px;
        }

        /* Table transition */
        .patients-table tbody {
            transition: opacity 0.3s ease;
        }
    </style>
'''

# Find the closing </body> tag and insert before it
if '</body>' in content:
    content = content.replace('</body>', js_code + '\n</body>')
    
    # Write back
    with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Successfully added dynamic dashboard JavaScript!")
else:
    print("ERROR: Could not find </body> tag")
