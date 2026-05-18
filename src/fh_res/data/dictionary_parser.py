import os

def load_variable_mapping(dictionary_path):
    """
    Parses VARIABLE_DICTIONARY.md to extract source_name_ru -> variable_name mapping
    and variable metadata (domain, model_role).
    """
    if not os.path.exists(dictionary_path):
        raise FileNotFoundError(f"Dictionary not found at {dictionary_path}")

    with open(dictionary_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    mapping = {}
    metadata = {}
    
    in_table = False
    for line in lines:
        if line.startswith('| `variable_name` |'):
            in_table = True
            continue
        if in_table and line.startswith('|---'):
            continue
        if in_table and line.startswith('| `'):
            parts = [p.strip() for p in line.split('|')]
            # Table has 12 columns, split by '|' yields ~13 parts (including empty first and last)
            if len(parts) > 10:
                var_name = parts[1].replace('`', '')
                source_name = parts[2]
                domain = parts[4]
                model_role = parts[7]
                
                # Some source names might be empty
                if source_name:
                    mapping[source_name] = var_name
                
                metadata[var_name] = {
                    'domain': domain,
                    'model_role': model_role,
                    'source_name': source_name
                }
                
        # If we hit an empty line after the table, we stop (optional, but good practice)
        elif in_table and line.strip() == '':
            pass # Tables can have gaps or end. Let's just keep looking in case there are multiple tables.

    return mapping, metadata

if __name__ == "__main__":
    # Test the parser
    m, md = load_variable_mapping("../../docs/VARIABLE_DICTIONARY.md")
    print(f"Loaded {len(m)} variable mappings.")
