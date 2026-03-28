"""
Run this script to fix smart/curly quotes in main.py that cause SyntaxErrors.
Replaces all Unicode curly quotes with plain ASCII quotes.
"""
import os
import re

file_path = os.path.join(os.path.dirname(__file__), "main.py")

with open(file_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

original = content

# Replace curly/smart double quotes with regular double quotes
content = content.replace('\u201c', '"')  # left double quotation mark "
content = content.replace('\u201d', '"')  # right double quotation mark "

# Replace curly/smart single quotes with regular single quotes
content = content.replace('\u2018', "'")  # left single quotation mark '
content = content.replace('\u2019', "'")  # right single quotation mark '

# Replace other problematic Unicode characters
content = content.replace('\u2013', '-')  # en dash
content = content.replace('\u2014', '--') # em dash
content = content.replace('\u2026', '...') # ellipsis

changes = sum(1 for a, b in zip(original, content) if a != b)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

if changes > 0:
    print(f"✅ Fixed {changes} smart quote/special character(s) in main.py")
else:
    print("ℹ️  No smart quotes found — check line 516 manually in VS Code")

print("Now try running main.py again.")
