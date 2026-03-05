import re

# Read the current file
with open('templates/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The AI section content (everything from the comment to the end of modals)
ai_section_pattern = r'\{% comment \%\}\s*\{% comment %\}\s*\{%\s*=================================================================\s*AI PORTRAIT INSIGHTS SECTION.*?\{% endblock %\}\s*\{% endif %\}'

# Find and remove the AI section that comes after {% endblock %}
# We want to move it inside the {% block content %}

# Split by {% endblock %} of content block
# The content block ends at the FIRST {% endblock %} that comes after the last </section>

# Let's find where the original content block ends
parts = content.split('{% endblock %}')

# parts[0] = everything before first {% endblock %} - this is inside block content
# parts[1] = everything after first {% endblock %} - this is where the AI section currently is

if len(parts) >= 2:
    # The first {% endblock %} closes the content block
    inside_block = parts[0]
    after_block = '{% endblock %}'.join(parts[1:])
    
    # Now find the AI section in the after_block
    ai_start = after_block.find('{% comment %}')
    if ai_start != -1:
        ai_section = after_block[ai_start:]
        
        # Find where the {% endif %} ends for the AI section
        # We need to find the matching {% endif %} for {% if user.is_authenticated %}
        # Let's find the structure: {% if user.is_authenticated %} ... {% endif %}
        
        # The AI section ends with {% endif %} that matches the user.is_authenticated
        # Find the last {% endif %} in the AI section
        ai_section_lines = ai_section.split('\n')
        
        # Remove from the end backwards until we find {% endif %} followed by nothing or }
        new_ai_lines = []
        found_endif = False
        for line in reversed(ai_section_lines):
            if not found_endif and '{% endif %}' in line:
                found_endif = True
            if found_endif:
                new_ai_lines.append(line)
            else:
                new_ai_lines.append(line)
        
        ai_section_fixed = '\n'.join(reversed(new_ai_lines))
        
        # Combine: inside block + AI section + {% endblock %}
        new_content = inside_block + '\n' + ai_section_fixed + '\n{% endblock %}'
        
        # Write back
        with open('templates/home.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("File fixed!")
    else:
        print("AI section not found after block")
else:
    print("Unexpected structure")

