import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding='utf-8')

dict_path = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\docs\VARIABLE_DICTIONARY.md")
content = dict_path.read_text(encoding="utf-8")

# Let's search for lines containing pressure-related terms
keywords = ["давление", "систолическое", "давл", "bp", "sbp", "pressure", "кср", "esd", "тзс", "задн", "posterior", "wall", "thickness"]

matched_lines = []
for line in content.splitlines():
    line_lower = line.lower()
    if any(re.search(r'\b' + re.escape(kw) + r'\b', line, re.IGNORECASE) for kw in keywords) or any(kw in line_lower for kw in ["давление", "кср", "тзс", "зс", "систол", "кдо", "ксо", "чсс"]):
        matched_lines.append(line)

print(f"Found {len(matched_lines)} matching lines in dictionary:")
for l in matched_lines[:100]:
    print(l)
