import json
import requests
from config import BOOKSTACK_API_BASE, BOOKSTACK_HEADERS

MAPPING_PATH = 'db/mapping.json'

def sync_book_mapping():
    # Upload existing mapping
    with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    mapping.setdefault('books', {})
    # Get books from BookStack
    resp = requests.get(f"{BOOKSTACK_API_BASE}/books?count=1000", headers=BOOKSTACK_HEADERS)
    if resp.status_code != 200:
        print("[sync_mapping] Erreur lors de la récupération des livres BookStack.")
        return
    books = resp.json().get('data', [])
    books_by_id = {str(b['id']): b for b in books}
    books_by_name = {b['name'].strip(): b for b in books}
    # Clean up the mapping and remove obsolete entries
    to_delete = []
    for key, val in mapping['books'].items():
        src_id, *_ = key.split('|')
        if str(val) not in books_by_id or str(src_id) not in books_by_id:
            print(f"[sync_mapping] Suppression du mapping obsolète : {key} -> {val}")
            to_delete.append(key)
    for key in to_delete:
        del mapping['books'][key]
    # Cleanup the mapping for chapters and pages
    if 'chapters' in mapping:
        # Récupérer tous les chapitres BookStack
        chapters_resp = requests.get(f"{BOOKSTACK_API_BASE}/chapters?count=1000", headers=BOOKSTACK_HEADERS)
        chapters = chapters_resp.json().get('data', []) if chapters_resp.status_code == 200 else []
        chapters_by_id = {str(ch['id']): ch for ch in chapters}
        to_delete = []
        for key, val in mapping['chapters'].items():
            src_id = key.split('|')[0]
            tgt_id = str(val)
            if src_id.isdigit() and src_id not in chapters_by_id:
                to_delete.append(key)
            if tgt_id.isdigit() and tgt_id not in chapters_by_id:
                to_delete.append(key)
        for key in set(to_delete):
            print(f"[sync_mapping] Suppression du mapping chapter obsolète : {key} -> {mapping['chapters'][key]}")
            del mapping['chapters'][key]
    # Nettoyer les pages
    if 'pages' in mapping:
        # Récupérer toutes les pages BookStack
        pages_resp = requests.get(f"{BOOKSTACK_API_BASE}/pages?count=1000", headers=BOOKSTACK_HEADERS)
        pages = pages_resp.json().get('data', []) if pages_resp.status_code == 200 else []
        pages_by_id = {str(pg['id']): pg for pg in pages}
        to_delete = []
        for key, val in mapping['pages'].items():
            src_id = key.split('|')[0]
            tgt_id = str(val)
            if src_id.isdigit() and src_id not in pages_by_id:
                to_delete.append(key)
            if tgt_id.isdigit() and tgt_id not in pages_by_id:
                to_delete.append(key)
        for key in set(to_delete):
            print(f"[sync_mapping] Suppression du mapping page obsolète : {key} -> {mapping['pages'][key]}")
            del mapping['pages'][key]
    # Nettoyer les pages_by_id
    if 'pages_by_id' in mapping:
        # Récupérer toutes les pages BookStack (déjà fait ci-dessus)
        to_delete = []
        for key, val in mapping['pages_by_id'].items():
            src_id = key.split('|')[0]
            tgt_id = str(val)
            if src_id.isdigit() and src_id not in pages_by_id:
                to_delete.append(key)
            if tgt_id.isdigit() and tgt_id not in pages_by_id:
                to_delete.append(key)
        for key in set(to_delete):
            print(f"[sync_mapping] Suppression du mapping pages_by_id obsolète : {key} -> {mapping['pages_by_id'][key]}")
            del mapping['pages_by_id'][key]
    # Pour chaque livre existant dans BookStack, essayer de détecter les traductions
    import re
    for book in books:
        name = book.get('name', '').strip()
        book_id = str(book.get('id'))
        # Détection par suffixe [lang]
        m = re.search(r'\[(\w{2,3})\]$', name)
        if m:
            lang = m.group(1)
            base_name = re.sub(r'\s*\[\w{2,3}\]\s*$', '', name).strip()
            for src in books:
                if src['name'].strip() == base_name and src['id'] != book['id']:
                    src_id = str(src['id'])
                    mapping['books'][f"{src_id}|{lang}"] = int(book_id)
        # Détection par similarité de nom (ex: Medulla Vue d'ensemble <-> Medulla Overview)
        if name.lower().endswith('overview'):
            for src in books:
                if src['id'] != book['id'] and (
                    'vue d\'ensemble' in src['name'].lower() or 'overview' in src['name'].lower()
                ):
                    src_id = str(src['id'])
                    if f"{src_id}|en" not in mapping['books']:
                        mapping['books'][f"{src_id}|en"] = int(book_id)
        if name.lower().endswith('step by step guide'):
            for src in books:
                if src['id'] != book['id'] and (
                    'schritt für schritt anleitung' in src['name'].lower() or 'step by step guide' in src['name'].lower()
                ):
                    src_id = str(src['id'])
                    if f"{src_id}|en" not in mapping['books']:
                        mapping['books'][f"{src_id}|en"] = int(book_id)
    # Sauvegarder le mapping enrichi et nettoyé
    with open(MAPPING_PATH, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print("[sync_mapping] Mapping enrichi et nettoyé avec les livres existants.")

if __name__ == "__main__":
    sync_book_mapping()
