import requests
from config import BOOKSTACK_API_BASE, BOOKSTACK_HEADERS

class BookStackBooksAPI:
    """Gestion des livres BookStack (CRUD, recherche, etc.)"""
    def list_books(self):
        resp = requests.get(f"{BOOKSTACK_API_BASE}/books?count=1000", headers=BOOKSTACK_HEADERS)
        if resp.status_code == 200:
            return resp.json().get('data', [])
        return []

    def get_book(self, book_id):
        resp = requests.get(f"{BOOKSTACK_API_BASE}/books/{book_id}", headers=BOOKSTACK_HEADERS)
        if resp.status_code == 200:
            return resp.json()
        return None

    def create_book(self, name, description=None):
        payload = {"name": name}
        if description:
            payload["description"] = description
        resp = requests.post(f"{BOOKSTACK_API_BASE}/books", headers=BOOKSTACK_HEADERS, json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        print(f"[API][Book] Erreur création livre : {resp.status_code} - {resp.text}")
        return None

    def update_book(self, book_id, fields):
        resp = requests.put(f"{BOOKSTACK_API_BASE}/books/{book_id}", headers=BOOKSTACK_HEADERS, json=fields)
        return resp.status_code == 200

    def delete_book(self, book_id):
        resp = requests.delete(f"{BOOKSTACK_API_BASE}/books/{book_id}", headers=BOOKSTACK_HEADERS)
        return resp.status_code == 204
