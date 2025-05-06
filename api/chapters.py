import requests
from config import BOOKSTACK_API_BASE, BOOKSTACK_HEADERS

class BookStackChaptersAPI:
    """Gestion des chapitres BookStack (CRUD, recherche, etc.)"""
    # BookStackChaptersAPI.py
    def list_chapters(self, book_id=None):
        resp = requests.get(f"{BOOKSTACK_API_BASE}/chapters?count=1000", headers=BOOKSTACK_HEADERS)
        if resp.status_code == 200:
            chapters = resp.json().get("data", [])
            if book_id is not None:
                return [ch for ch in chapters if ch.get("book_id") == book_id]
            return chapters
        return []


    def get_chapter(self, chapter_id):
        
        resp = requests.get(f"{BOOKSTACK_API_BASE}/chapters/{chapter_id}", headers=BOOKSTACK_HEADERS)
        if resp.status_code == 200:
            return resp.json()
        return None

    def create_chapter(self, book_id, name, description=None):
        payload = {"book_id": book_id, "name": name}
        if description:
            payload["description"] = description
        resp = requests.post(f"{BOOKSTACK_API_BASE}/chapters", headers=BOOKSTACK_HEADERS, json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        print(f"[API][Chapter] Erreur création chapitre : {resp.status_code} - {resp.text}")
        return None

    def update_chapter(self, chapter_id, fields):
        resp = requests.put(f"{BOOKSTACK_API_BASE}/chapters/{chapter_id}", headers=BOOKSTACK_HEADERS, json=fields)
        return resp.status_code == 200

    def delete_chapter(self, chapter_id):
        resp = requests.delete(f"{BOOKSTACK_API_BASE}/chapters/{chapter_id}", headers=BOOKSTACK_HEADERS)
        return resp.status_code == 204
