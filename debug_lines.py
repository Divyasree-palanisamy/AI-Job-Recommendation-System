with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check the specific lines and columns mentioned
check_points = [
    (3444, [14, 16, 19, 33, 37, 80]),
    (3446, [14, 23, 80]),
    (175, [13])
]

for line_num, cols in check_points:
    if line_num <= len(lines):
        line = lines[line_num - 1].rstrip()
        print(f'Line {line_num}: {repr(line)}')
        for col in cols:
            if col <= len(line) and col > 0:
                char = line[col-1]
                print(f'  Column {col}: \"{char}\" (ord: {ord(char)})')
        print()
    else:
        print(f'Line {line_num}: NOT FOUND (file has {len(lines)} lines)')