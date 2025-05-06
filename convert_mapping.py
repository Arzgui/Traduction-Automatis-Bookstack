import json

def convert_flat_to_nested_mapping(mapping_path='db/mapping.json'):
    with open(mapping_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = {"books": {}, "chapters": {}, "pages": {}, "pages_by_id": data.get("pages_by_id", {})}

    for section in ("books", "chapters", "pages"):
        for flat_key, target_id in data.get(section, {}).items():
            if '|' in flat_key:
                source_id, lang = flat_key.split('|', 1)
                new_data[section].setdefault(source_id, {})[lang] = target_id
            else:
                print(f"⚠️ Clé non standard ignorée dans '{section}': {flat_key}")

    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print("✅ Fichier mapping.json converti au format imbriqué.")

if __name__ == "__main__":
    convert_flat_to_nested_mapping()
    # convert_flat_to_nested_mapping('db/test_mapping.json')
    # convert_flat_to_nested_mapping('db/mapping.json')