"""
Script to make patient dashboard sections dynamic
Safely updates HTML file to remove static data
"""

def update_dashboard():
    file_path = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Update Health Trends section (lines ~725-736)
    old_health_trends = '''                <!-- Health Trends -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-chart-line"></i> Health Trends
                        </div>
                        <a href="#" class="card-action">View All</a>
                    </div>
                    <div style="height: 300px;">
                        <canvas id="healthTrendsChart"></canvas>
                    </div>
                </div>'''
    
    new_health_trends = '''                <!-- Health Trends -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-chart-line"></i> Health Trends
                        </div>
                        <a href="#" class="card-action">View All</a>
                    </div>
                    {% if dashboard.has_history %}
                    <div style="height: 300px;">
                        <canvas id="healthTrendsChart"></canvas>
                    </div>
                    {% else %}
                    <div style="text-align: center; padding: 40px 20px; color: #666;">
                        <i class="fas fa-chart-bar" style="font-size: 48px; margin-bottom: 20px; color: #0d9488;"></i>
                        <h3 style="margin-bottom: 15px; color: #333;">No Health Trends Data</h3>
                        <p style="margin-bottom: 20px;">Upload your lab reports over time to see your health trends.</p>
                        <button onclick="document.getElementById('labUpload').click()" 
                                style="background: #0d9488; color: white; border: none; padding: 12px 24px; 
                                       border-radius: 8px; cursor: pointer; font-weight: 500;">
                            <i class="fas fa-upload"></i> Upload Lab Report
                        </button>
                    </div>
                    {% endif %}
                </div>'''
    
    content = content.replace(old_health_trends, new_health_trends)
    
    # 2. Update chart JavaScript to check if element exists
    old_chart_js = '''        // Health Trends Chart
        const ctx = document.getElementById('healthTrendsChart').getContext('2d');
        const healthTrendsChart = new Chart(ctx, {'''
    
    new_chart_js = '''        // Health Trends Chart - only initialize if element exists
        const chartElement = document.getElementById('healthTrendsChart');
        if (chartElement) {
            const ctx = chartElement.getContext('2d');
            const healthTrendsChart = new Chart(ctx, {'''
    
    content = content.replace(old_chart_js, new_chart_js)
    
    # Close the if statement at the end of chart initialization
    old_chart_end = '''            }
        });

        // File Upload Handler'''
    
    new_chart_end = '''            }
            });
        }

        // File Upload Handler'''
    
    content = content.replace(old_chart_end, new_chart_end)
    
    print("✅ Updated Health Trends section")
    print("✅ Updated chart JavaScript")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ All updates completed successfully!")
    print("File saved:", file_path)

if __name__ == '__main__':
    update_dashboard()
