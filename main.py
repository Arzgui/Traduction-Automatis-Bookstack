from api.books import BookStackBooksAPI
from api.chapters import BookStackChaptersAPI
from api.pages import BookStackPagesAPI
from translation.sync import SyncManager
from translation.translate import TranslationService  # Import de la classe TranslationService

def main():
    books_api = BookStackBooksAPI()
    chapters_api = BookStackChaptersAPI()
    pages_api = BookStackPagesAPI()
    sync = SyncManager()

    # Création de l'instance du service de traduction
    translation_service = TranslationService()

    print("\n--- Traduction/MAJ BookStack (mode simplifié) ---")
    print("1. Traduire un livre entier")
    print("2. Traduire un chapitre")
    print("3. Traduire une page")
    print("4. Mettre à jour un livre")
    print("5. Mettre à jour un chapitre")
    print("6. Mettre à jour une page")
    choix = input("\nVotre choix (1-6): ").strip()

    if choix not in {'1', '2', '3', '4', '5', '6'}:
        print("Choix invalide.")
        return

    books = books_api.list_books()
    if not books:
        print("Aucun livre trouvé.")
        return

    print("\nLivres disponibles :")
    for book in books:
        print(f"Book ID: {book.get('id')}, Name: {book.get('name')}")
    book_id = input("\nID du livre à utiliser: ").strip()
    if not book_id.isdigit():
        print("ID de livre invalide.")
        return
    book_id = int(book_id)

    if choix == '1':  # Traduction du livre entier
        langs = input("Langues cibles (ex: en,de,es): ").strip()
        if not langs:
            print("Aucune langue cible spécifiée.")
            return
        target_langs = [l.strip() for l in langs.split(',') if l.strip()]
        sync.sync_book(book_id, target_langs)
        return

    chapters = chapters_api.list_chapters(book_id)
    print("\nChapitres du livre:")
    for ch in chapters:
        print(f"Chapitre ID: {ch.get('id')}, Name: {ch.get('name')}")

    if choix in {'2', '5'}:
        chapter_id = input("ID du chapitre: ").strip()
        if not chapter_id.isdigit():
            print("ID de chapitre invalide.")
            return
        chapter_id = int(chapter_id)

    pages = pages_api.list_pages(book_id=book_id)
    print("\nPages du livre:")
    for page in pages:
        print(f"Page ID: {page.get('id')}, Name: {page.get('name')}")

    if choix in {'3', '6'}:
        page_id = input("ID de la page: ").strip()
        if not page_id.isdigit():
            print("ID de page invalide.")
            return
        page_id = int(page_id)

    # Traduction du chapitre ou de la page
    if choix == '2':
        target_lang = input("Langue cible pour le chapitre (ex: en): ").strip()
        if not target_lang:
            print("Aucune langue cible spécifiée.")
            return
        chapter = chapters_api.get_chapter(chapter_id)
        chapter_text = chapter.get('text')  # Assurez-vous que votre API retourne un champ texte
        translated_text = translation_service.translate_text(chapter_text, target_lang)
        chapters_api.update_chapter(chapter_id, {'text': translated_text})  # Mise à jour du chapitre

    elif choix == '3':
        target_lang = input("Langue cible pour la page (ex: en): ").strip()
        if not target_lang:
            print("Aucune langue cible spécifiée.")
            return
        page = pages_api.get_page(page_id)
        page_html = page.get('html')  # Assurez-vous que votre API retourne un champ HTML
        translated_html = translation_service.translate_html(page_html, target_lang)
        pages_api.update_page(page_id, {'html': translated_html})  # Mise à jour de la page

    elif choix == '4':
        new_name = input("Nouveau nom du livre (laisser vide pour ne pas changer): ").strip()
        new_desc = input("Nouvelle description (laisser vide pour ne pas changer): ").strip()
        update_fields = {}
        if new_name:
            update_fields['name'] = new_name
        if new_desc:
            update_fields['description'] = new_desc
        if update_fields:
            books_api.update_book(book_id, update_fields)
            print("Livre mis à jour.")
        else:
            print("Aucune modification à appliquer.")
    elif choix == '5':
        new_name = input("Nouveau nom du chapitre (laisser vide pour ne pas changer): ").strip()
        new_desc = input("Nouvelle description (laisser vide pour ne pas changer): ").strip()
        update_fields = {}
        if new_name:
            update_fields['name'] = new_name
        if new_desc:
            update_fields['description'] = new_desc
        if update_fields:
            chapters_api.update_chapter(chapter_id, update_fields)
            print("Chapitre mis à jour.")
        else:
            print("Aucune modification à appliquer.")
    elif choix == '6':
        new_html = input("Nouveau contenu HTML (laisser vide pour ne pas changer): ").strip()
        if new_html:
            pages_api.update_page(page_id, {"html": new_html})
            print("Page mise à jour.")
        else:
            print("Aucune modification à appliquer.")

if __name__ == "__main__":
    main()
