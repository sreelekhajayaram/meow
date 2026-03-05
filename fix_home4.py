import os

# Change to the project directory
os.chdir('c:/Users/MY PC/Downloads/artworks_ofsree-main')

# Read the current file
with open('templates/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first {% endblock %} - this closes the {% block content %}
first_endblock_pos = 8255

# Everything before the first {% endblock %}
before_content_end = content[:first_endblock_pos]

# Everything after the first {% endblock %}
after_content_end = content[first_endblock_pos:]

# Find the AI section in the 'after' part - starts with {% comment %}
ai_start = after_content_end.find('{% comment %}')

if ai_start != -1:
    # Extract the AI section
    ai_section = after_content_end[ai_start:]
    
    # Find {% block extra_js %}
    extrablock = ai_section.find('{% block extra_js %}')
    
    if extrablock != -1:
        # The AI section is everything before {% block extra_js %}
        ai_section_clean = ai_section[:extrablock]
        
        # Now reconstruct - put AI section inside content block
        new_content = before_content_end + '\n' + ai_section_clean + '\n{% endblock %}\n' + '{% block extra_js %}' + ai_section[extrablock + 17:]
        
        # Write back
        with open('templates/home.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("File fixed successfully!")
    else:
        print("Could not find extra_js block")
else:
    print("Could not find AI section")

