with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== CHECKING EXACT LINE LENGTHS AND CHARACTERS ===')

# Check the problematic lines
check_lines = [175, 3444, 3446]

for line_num in check_lines:
    if line_num <= len(lines):
        line = lines[line_num - 1].rstrip()
        print(f'\nLine {line_num}:')
        print(f'  Length: {len(line)} characters')
        print(f'  Content: {repr(line)}')

        # Show character codes for specific positions
        cols_to_check = []
        if line_num == 175:
            cols_to_check = [13]
        elif line_num == 3444:
            cols_to_check = [14, 16, 19, 33, 37, 80]
        elif line_num == 3446:
            cols_to_check = [14, 23, 80]

        for col in cols_to_check:
            if col <= len(line):
                char = line[col-1]
                print(f'  Column {col}: "{char}" (ASCII: {ord(char)})')
            else:
                print(f'  Column {col}: OUT OF BOUNDS (line only has {len(line)} chars)')
    else:
        print(f'Line {line_num}: DOES NOT EXIST')

print('\n=== CHECKING FOR HIDDEN CHARACTERS ===')
# Check for potential hidden characters
for line_num in check_lines:
    if line_num <= len(lines):
        line = lines[line_num - 1]
        hidden_chars = []
        for i, char in enumerate(line):
            if ord(char) > 127 or (ord(char) < 32 and ord(char) not in [9, 10, 13]):  # Tab, LF, CR are OK
                hidden_chars.append((i+1, ord(char), repr(char)))

        if hidden_chars:
            print(f'Line {line_num} hidden characters: {hidden_chars}')
        else:
            print(f'Line {line_num}: No hidden characters found')