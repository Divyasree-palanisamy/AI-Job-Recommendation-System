with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check specific lines mentioned by user
lines_to_check = [
    (2356, [60, 90]),
    (2786, [56, 81, 91, 109, 179, 185]),
    (2913, [48, 111]),
    (2914, [41, 87]),
    (2915, [42, 107]),
    (2916, [43, 68, 81, 101, 111]),
    (2943, [102, 120, 122]),
    (3244, [56, 81, 91, 109, 179, 185]),
    (3296, [96, 158, 161]),
    (3415, [14, 16, 19, 33, 80]),
    (175, [13])
]

print("=== CHECKING SPECIFIC LINE ERRORS ===")
for line_num, cols in lines_to_check:
    if line_num <= len(lines):
        line = lines[line_num - 1].rstrip()
        print(f'Line {line_num}: {line}')
        for col in cols:
            if col <= len(line) and col > 0:
                char = line[col-1]
                print(f'  Column {col}: "{char}"')
        print()
    else:
        print(f'Line {line_num}: NOT FOUND (file has {len(lines)} lines)')
        print()

print("=== VALIDATION SUMMARY ===")
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

css_open = content.count('{')
css_close = content.count('}')
print(f'CSS braces: {css_open} open, {css_close} close - {"Balanced" if css_open == css_close else "Unbalanced"}')

# Check for Jinja2 in style attributes
import re
jinja_in_style = re.findall(r'style="[^"]*\{\{[^}]+\}\}[^"]*"', content)
print(f'Jinja2 expressions in style attributes: {len(jinja_in_style)}')

if jinja_in_style:
    print("POTENTIAL ISSUES FOUND:")
    for i, match in enumerate(jinja_in_style[:5]):
        print(f'  {i+1}: {match[:80]}...')
else:
    print("No Jinja2 expressions found in style attributes")