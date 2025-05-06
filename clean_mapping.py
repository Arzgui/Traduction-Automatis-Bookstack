# clean_mapping.py
from api.mapping import MappingManager
from api.books import BookStackBooksAPI
from api.chapters import BookStackChaptersAPI
from api.pages import BookStackPagesAPI

def get_valid_ids():
    books_api = BookStackBooksAPI()
    chapters_api = BookStackChaptersAPI()
    pages_api = BookStackPagesAPI()

    valid_books = {str(book['id']) for book in books_api.list_books()}
    valid_chapters = set()
    valid_pages = set()

    for book_id in valid_books:
        for chapter in chapters_api.list_chapters(book_id):
            valid_chapters.add(str(chapter['id']))
        for page in pages_api.list_pages(book_id=book_id):
            valid_pages.add(str(page['id']))

    return valid_books, valid_chapters, valid_pages

def test_mapping_loading():
    manager = MappingManager()
    # Upload the mapping to test if it loads correctly
    mapping = manager.load_mapping()
    print("Mapping chargé avec succès :")
    print(mapping)

if __name__ == "__main__":
    print("Récupération des éléments valides dans BookStack...")
    valid_books, valid_chapters, valid_pages = get_valid_ids()

    print("Démarrage du nettoyage du mapping...")

    test_mapping_loading()
    
    # Create a new instance of MappingManager to clean the mapping
    manager = MappingManager()
    manager.clean_mapping()
    
    print("Nettoyage terminé.")
    print("Mapping mis à jour et enregistré.")
    print("Vérification du mapping après nettoyage :")