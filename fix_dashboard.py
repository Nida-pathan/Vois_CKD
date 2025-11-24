# Script to add appointments section to doctor_dashboard.html
with open('templates/doctor_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "    </div>" followed by "</div>" (around line 619-620)
insert_index = None
for i, line in enumerate(lines):
    if i > 600 and line.strip() == '</div>' and i > 0:
        # Check if previous line is "    </div>"
        if lines[i-1].strip() == '</div>':
            insert_index = i
            break

if insert_index:
    # Appointments section to insert
    appointments_section = '''
    <!-- Appointments Section -->
    <div class="card" style="margin-top: 25px;">
        <div class="card-header">
            <div class="card-title">
                <i class="fas fa-calendar-alt"></i> Appointments
            </div>
        </div>
        {% if appointments %}
        <div style="overflow-x: auto;">
            <table class="patients-table">
                <thead>
                    <tr>
                        <th>Patient</th>
                        <th>Preferred Date</th>
                        <th>Preferred Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for apt in appointments %}
                    <tr>
                        <td>{{ apt.patient }}</td>
                        <td>{{ apt.preferred_date }}</td>
                        <td>{{ apt.preferred_time }}</td>
                        <td>
                            <span class="badge badge-{{ 'low' if apt.status == 'confirmed' else 'moderate' }}">
                                {{ apt.status }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="empty-state">
            <p>No appointments scheduled.</p>
        </div>
        {% endif %}
    </div>
'''
    
    # Insert the appointments section
    lines.insert(insert_index, appointments_section)
    
    # Write back to file
    with open('templates/doctor_dashboard.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Successfully added appointments section at line {insert_index}")
else:
    print("Could not find insertion point")
