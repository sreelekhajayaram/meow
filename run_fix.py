import os
os.chdir('c:/Users/MY PC/Downloads/artworks_ofsree-main')
with open('templates/home.html', 'r', encoding='utf-8') as f:
    content = f.read()
first_endblock_pos = 8255
before_content_end = content[:first_endblock_pos]
after_content_end = content[first_endblock_pos:]
ai_start = after_content_end.find('{% comment %}')
if ai_start != -1:
    ai_section = after_content_end[ai_start:]
    extrablock = ai_section.find('{% block extra_js %}')
    if extrablock != -1:
        ai_section_clean = ai_section[:extrablock]
        new_content = before_content_end + '\n' + ai_section_clean + '\n{% endblock %}\n' + '{% block extra_js %}' + ai_section[extrablock + 17:]
        with open('templates/home.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("File fixed successfully!")
    else:
        print("Could not find extra_js block")
else:
    print("Could not find AI section")

