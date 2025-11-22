"""
Update patient dashboard Diet & Lifestyle section to show AI teaser
"""

def update_dashboard_ai_section():
    file_path = r'c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\templates\patient_dashboard.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the Diet & Lifestyle section
    old_section = '''                <!-- Diet & Lifestyle Changes -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-apple-alt"></i> Diet & Lifestyle
                        </div>
                        <a href="{{ url_for('diet_plan') }}" class="card-action">View Plan</a>
                    </div>
                    {% for recommendation in dashboard.lifestyle_recommendations %}
                    <div class="lifestyle-item">
                        <div class="lifestyle-icon">
                            <i class="fas {{ recommendation.icon }}"></i>
                        </div>
                        <div class="lifestyle-content">
                            <div class="lifestyle-title">{{ recommendation.title }}</div>
                            <div class="lifestyle-description">{{ recommendation.description }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>'''
    
    new_section = '''                <!-- AI-Powered Diet & Lifestyle -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-robot"></i> AI-Powered Diet & Lifestyle
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 30px 20px;">
                        <div style="font-size: 48px; margin-bottom: 20px;">
                            <i class="fas fa-magic" style="color: #0d9488;"></i>
                        </div>
                        <h3 style="margin-bottom: 15px; color: #333;">Get Your Personalized CKD Plan</h3>
                        <p style="color: #666; margin-bottom: 25px; line-height: 1.6; font-size: 14px;">
                            Our AI will create a custom plan just for you including:<br>
                            ✓ Low-sodium diet plan  ✓ Weekly recipes  ✓ Exercise routine<br>
                            ✓ Food swaps  ✓ Hydration guide  ✓ Daily routine tips
                        </p>
                        <a href="{{ url_for('ai_lifestyle_plan') }}" 
                           style="display: inline-block; background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); 
                                  color: white; padding: 15px 30px; border-radius: 12px; text-decoration: none;
                                  font-weight: 600; box-shadow: 0 4px 15px rgba(13, 148, 136, 0.3); transition: all 0.3s;">
                            <i class="fas fa-sparkles"></i> Generate My AI Plan
                        </a>
                        <p style="font-size: 11px; color: #999; margin-top: 15px;">
                            AI-generated recommendations are educational and should be reviewed with your healthcare provider
                        </p>
                    </div>
                </div>'''
    
    if old_section in content:
        content = content.replace(old_section, new_section)
        print("✅ Updated Diet & Lifestyle section to AI-powered version")
    else:
        print("⚠️  Could not find exact section to replace")
        print("   The section may have already been modified")
        return False
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Dashboard updated with AI teaser!")
    print("File saved:", file_path)
    return True

if __name__ == '__main__':
    update_dashboard_ai_section()
