import sys
from pathlib import Path
import json

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords")
notebooks_dir = PROJECT_ROOT / "notebooks"

keywords = ["posterior_wall", "thickness", "stress", "напряжение", "сад", "кср", "зслж"]

for nb_path in notebooks_dir.glob("*.ipynb"):
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        
        matches = []
        for cell_idx, cell in enumerate(nb.get("cells", [])):
            cell_type = cell.get("cell_type", "")
            source = cell.get("source", [])
            source_str = "".join(source)
            
            found = [kw for kw in keywords if kw in source_str.lower()]
            if found:
                matches.append((cell_idx, cell_type, found))
        
        if matches:
            print(f"Notebook: {nb_path.name} - found {len(matches)} matching cells:")
            for idx, ctype, f_kws in matches[:5]:
                print(f"  Cell {idx} ({ctype}): {f_kws}")
    except Exception as e:
        print(f"Error reading {nb_path.name}: {e}")
