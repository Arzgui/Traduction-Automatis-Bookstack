import logging
import requests
from config import BOOKSTACK_API_BASE, BOOKSTACK_HEADERS

class BookStackPagesAPI:
    """Gestion des pages BookStack (CRUD, recherche, etc.)"""
    
    def list_pages(self, book_id=None, chapter_id=None):
        """Liste les pages en fonction du livre ou du chapitre."""
        if chapter_id:
            resp = requests.get(f"{BOOKSTACK_API_BASE}/chapters/{chapter_id}/pages?count=1000", headers=BOOKSTACK_HEADERS)
        elif book_id:
            resp = requests.get(f"{BOOKSTACK_API_BASE}/books/{book_id}/pages?count=1000", headers=BOOKSTACK_HEADERS)
        else:
            resp = requests.get(f"{BOOKSTACK_API_BASE}/pages?count=1000", headers=BOOKSTACK_HEADERS)
        
        if resp.status_code == 200:
            return resp.json().get('data', [])
        return []

    def get_page(self, page_id):
        """Récupère les informations d'une page spécifique."""
        resp = requests.get(f"{BOOKSTACK_API_BASE}/pages/{page_id}", headers=BOOKSTACK_HEADERS)
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_book(self, book_id):
        """Vérifie si un livre avec l'ID donné existe."""
        resp = requests.get(f"{BOOKSTACK_API_BASE}/books/{book_id}", headers=BOOKSTACK_HEADERS)
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_chapter(self, chapter_id):
        """Vérifie si un chapitre avec l'ID donné existe."""
        resp = requests.get(f"{BOOKSTACK_API_BASE}/chapters/{chapter_id}", headers=BOOKSTACK_HEADERS)
        if resp.status_code == 200:
            return resp.json()
        return None

    def create_page(self, book_id, chapter_id, name, html, lang, source_page_id):
        existing_id = self.mapping.get_page(source_page_id, lang)
        if existing_id:
            logging.warning(f"[PAGES] Tentative de recreer une page existante (ID {existing_id}) pour {lang}")
            return None
        payload = {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "name": name,
        "html": html,
        "source_page_id": source_page_id,
    }
        response = requests.post(
        f"{self.api_base}/pages",
        headers=self.headers,
        json=payload
    )
        response.raise_for_status()
        return response.json()


    def update_page(self, page_id, name, html, lang):
        payload = {
        "name": name,
        "html": html
    }
        response = requests.put(
        f"{self.api_base}/pages/{page_id}",
        headers=self.headers,
        json=payload
    )
        response.raise_for_status()
        return response.json()



    def delete_page(self, page_id):
        """Supprime une page spécifique."""
        resp = requests.delete(f"{BOOKSTACK_API_BASE}/pages/{page_id}", headers=BOOKSTACK_HEADERS)
        return resp.status_code == 204
