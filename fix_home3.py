# Read the current file
with open('templates/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first {% endblock %} - this closes the {% block content %}
first_endblock_pos = 8255  # We found this from the regex

# Everything before the first {% endblock %}
before_content_end = content[:first_endblock_pos]

# Everything after the first {% endblock %}
after_content_end = content[first_endblock_pos:]

# Find the AI section in the 'after' part - starts with {% comment %}
ai_start = after_content_end.find('{% comment %}')

if ai_start != -1:
    # Extract the AI section
    ai_section = after_content_end[ai_start:]
    
    # The AI section should end with {% endif %} that closes the {% if user.is_authenticated %}
    # Find the pattern - we need to find where {% endif %} appears that matches
    # Let's trace through - find the structure:
    # {% if user.is_authenticated %} ... {% endif %}
    
    # Count the {% if %} and {% endif %} to find the matching one
    # We need to find the LAST {% endif %} that closes the user.is_authenticated
    
    # Let's find all {% if %} and {% endif %} positions
    import re
    if_positions = [m.start() for m in re.finditer(r'\{% if', ai_section)]
    endif_positions = [m.start() for m in re.finditer(r'\{% endif %\}', ai_section)]
    
    print(f"Found {len(if_positions)} {% if %} tags")
    print(f"Found {len(endif_positions)} {% endif %} tags")
    
    # We want the last {% endif %} since we only have one {% if %}
    # But there might be other {% if %} inside HTML (like {% if categories %})
    # Let's look at the raw text
    
    # Simply: find the LAST {% endif %} in the AI section
    # and take everything up to and including it
    
    # More robust: find the {% endif %} that appears AFTER the last meaningful content
    # Let's just manually find where the AI section ends by looking at the structure
    
    # The AI section should end with: {% endblock %} followed by {% endif %}
    # Wait, we have {% endblock %} inside extra_js block too
    
    # Let me look at the text more carefully
    # From our read_file output, the structure after {% endblock %} is:
    # {% endblock %}
    # {% comment %}
    # ... AI section ...
    # {% endblock %}
    # {% endif %}
    # {% block extra_js %}
    # ...
    # {% endblock %}
    
    # So the AI section starts at {% comment %} and ends at {% endif %} (before {% block extra_js %})
    
    # Find {% block extra_js %}
    extrablock = ai_section.find('{% block extra_js %}')
    
    if extrablock != -1:
        # The AI section is everything before {% block extra_js %}
        ai_section_clean = ai_section[:extrablock]
        
        # Now reconstruct
        new_content = before_content_end + '\n' + ai_section_clean + '\n{% endblock %}\n' + '{% block extra_js %}' + ai_section[extrablock + len('{% block extra_js %}'):]
        
        # Write back
        with open('templates/home.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("File fixed successfully!")
        print(f"AI section length: {len(ai_section_clean)}")
    else:
        print("Could not find {% block extra_js %}")
else:
    print("Could not find AI section start")

