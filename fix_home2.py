# Read the current file
with open('templates/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position of the first {% endblock %}
first_endblock = content.find('{% endblock %}')

# Find the second {% endblock %}
second_endblock = content.find('{% endblock %}', first_endblock + 1)

# Find the third {% endblock %}
third_endblock = content.find('{% endblock %}', second_endblock + 1)

print(f"First {% endblock %} at: {first_endblock}")
print(f"Second {% endblock %} at: {second_endblock}")
print(f"Third {% endblock %} at: {third_endblock}")

# Extract the sections
before_first = content[:first_endblock]
between = content[first_endblock:second_endblock]
after_second = content[second_endblock:]

print("\n=== Between first and second ===")
print(between[:200])
print("\n=== After second ===") 
print(after_second[:300])

