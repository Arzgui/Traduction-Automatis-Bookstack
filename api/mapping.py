import json
import logging
import copy
from difflib import SequenceMatcher

from api.books import BookStackBooksAPI
from api.chapters import BookStackChaptersAPI
from api.pages import BookStackPagesAPI
from translation.translate import TranslationService


class MappingManager:
    def __init__(self, mapping_path='db/mapping.json'):
        self.mapping_path = mapping_path
        self.mapping = self.load_mapping()
        self.book_api = BookStackBooksAPI()
        self.chapter_api = BookStackChaptersAPI()
        self.page_api = BookStackPagesAPI()
        self.translation_service = TranslationService()

    def is_empty(self) -> bool:
        return not self.mapping or all(not v for v in self.mapping.values())

    def load_mapping(self):
        try:
            with open(self.mapping_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
                logging.info(f"[MAPPING] Mapping chargé depuis {self.mapping_path}.")
                return mapping
        except FileNotFoundError:
            logging.warning(f"[MAPPING] Aucun fichier trouvé à {self.mapping_path}, démarrage avec un mapping vide.")
            return {}
        except UnicodeDecodeError:
            logging.warning(f"[MAPPING] Échec du décodage UTF-8, tentative avec Latin-1...")
            try:
                with open(self.mapping_path, 'r', encoding='latin-1') as f:
                    data = f.read()
                    mapping = json.loads(data)
                    logging.info(f"[MAPPING] Mapping chargé depuis {self.mapping_path} via Latin-1.")
                    return mapping
            except Exception as e:
                logging.error(f"[MAPPING] Impossible de charger le mapping en Latin-1 : {e}")
                return {}
        except json.JSONDecodeError:
            logging.error(f"[MAPPING] Erreur JSON lors de la lecture du fichier {self.mapping_path}, retour d'un mapping vide.")
            return {}
        except Exception as e:
            logging.error(f"[MAPPING] Erreur inconnue lors du chargement du mapping : {e}")
            return {}

    def save_mapping(self):
        try:
            with open(self.mapping_path, 'w', encoding='utf-8') as f:
                json.dump(self.mapping, f, indent=4, ensure_ascii=False)
                logging.info(f"[MAPPING] Mapping sauvegardé dans {self.mapping_path}.")
        except Exception as e:
            logging.error(f"[MAPPING] Erreur lors de la sauvegarde du fichier de mapping : {e}")

    # ---- BOOKS ----

    def get_mapped_book(self, source_id, lang):
        return (
            self.mapping
            .get("books", {})
            .get(str(source_id), {})
            .get("translations", {})
            .get(lang)
        )

    def set_mapped_book(self, source_id, lang, target_id):
        book = (
            self.mapping
            .setdefault("books", {})
            .setdefault(str(source_id), {})
        )
        book.setdefault("translations", {})[lang] = target_id
        self.save_mapping()

    def get_book(self, source_id, lang):
        return self.get_mapped_book(source_id, lang)

    # ---- CHAPTERS ----

    def get_mapped_chapter(self, source_id, lang):
        return (
            self.mapping
            .get("chapters", {})
            .get(str(source_id), {})
            .get("translations", {})
            .get(lang)
        )

    def set_mapped_chapter(self, source_id, lang, target_id):
        chapter = (
            self.mapping
            .setdefault("chapters", {})
            .setdefault(str(source_id), {})
        )
        chapter.setdefault("translations", {})[lang] = target_id
        self.save_mapping()

    def get_chapter(self, source_id, lang):
        return self.get_mapped_chapter(source_id, lang)

    # ---- PAGES ----

    def get_mapped_page(self, source_id, lang):
        return (
            self.mapping
            .get("pages", {})
            .get(str(source_id), {})
            .get("translations", {})
            .get(lang)
        )

    def set_mapped_page(self, source_id, lang, target_id):
        page = (
            self.mapping
            .setdefault("pages", {})
            .setdefault(str(source_id), {})
        )
        page.setdefault("translations", {})[lang] = target_id
        if 'chapter_id' not in page or 'book_id' not in page:
            try:
                src_page = self.page_api.get_page(source_id)
                page['chapter_id'] = src_page.get('chapter_id')
                page['book_id'] = src_page.get('book_id')
            except Exception:
                pass
        self.save_mapping()

    def get_page(self, source_id, lang):
        logging.info(f"[MAPPING] Appel de get_page({source_id}, {lang})")
        return self.get_mapped_page(source_id, lang)

    # ---- LISTING ----

    def get_chapters_of_book(self, book_id):
        return self.chapter_api.list_chapters(book_id)

    def get_pages_of_chapter(self, chapter_id):
        return self.page_api.list_pages(chapter_id=chapter_id)

    # ---- CLEANUP & LINKING ----

    def similar(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _match_by_title(self, source_dict, langs=["en", "de", "fr"], threshold=0.8):
        items = list(source_dict.items())
        for i, (src_id, src_data) in enumerate(items):
            src_title = src_data.get("title", "")
            for tgt_id, tgt_data in items[i + 1:]:
                # Skip matching if same contextual parent (for chapters/pages)
                if (
                    "book_id" in src_data and "book_id" in tgt_data
                    and src_data.get("book_id") == tgt_data.get("book_id")
                ):
                    continue
                tgt_title = tgt_data.get("title", "")
                for lang in langs:
                    try:
                        translated = self.translation_service.translate_text(src_title, lang)
                        trans_lower = translated.strip().lower()
                        tgt_lower = tgt_title.strip().lower()
                        # exact or fuzzy match
                        if trans_lower == tgt_lower or self.similar(trans_lower, tgt_lower) >= threshold:
                            src_data.setdefault("translations", {})[lang] = int(tgt_id)
                            break
                    except Exception as e:
                        logging.warning(f"Traduction échouée : {src_title} -> {lang} : {e}")

    def clean_mapping(self):
        print("Nettoyage et reconstruction du mapping...")
        old_mapping = copy.deepcopy(self.mapping)
        books = self.book_api.list_books()
        chapters = []
        pages = []

        self.mapping = {
            "books": {},
            "chapters": {},
            "pages": {},
            "pages_by_id": {}
        }

        for book in books:
            b_id = str(book["id"])
            old_trans = old_mapping.get("books", {}).get(b_id, {}).get("translations", {})
            self.mapping["books"][b_id] = {
                "title": book.get("name"),
                "slug": book.get("slug"),
                "translations": old_trans.copy()
            }
            for chap in self.chapter_api.list_chapters(book["id"]):
                c_id = str(chap["id"])
                old_c_trans = old_mapping.get("chapters", {}).get(c_id, {}).get("translations", {})
                self.mapping["chapters"][c_id] = {
                    "title": chap.get("name"),
                    "book_id": chap.get("book_id"),
                    "translations": old_c_trans.copy()
                }
                chapters.append(chap)

            for page in self.page_api.list_pages(book_id=book["id"]):
                p_id = str(page["id"])
                old_p_trans = old_mapping.get("pages", {}).get(p_id, {}).get("translations", {})
                self.mapping["pages"][p_id] = {
                    "title": page.get("name"),
                    "chapter_id": page.get("chapter_id"),
                    "book_id": page.get("book_id"),
                    "translations": old_p_trans.copy()
                }
                self.mapping["pages_by_id"][p_id] = {
                    "book_id": page.get("book_id"),
                    "chapter_id": page.get("chapter_id"),
                    "page_id": page.get("id")
                }
                pages.append(page)

        self._match_by_title(self.mapping["books"])
        self._match_by_title(self.mapping["chapters"])
        self._match_by_title(self.mapping["pages"])

        self.save_mapping()
        print("Mapping nettoyé et reconstruit.")

    def remove_page(self, source_id, lang):
        page_entry = self.mapping.get("pages", {}).get(str(source_id))
        if page_entry and 'translations' in page_entry and lang in page_entry['translations']:
            del page_entry['translations'][lang]
            if not page_entry['translations']:
                del self.mapping["pages"][str(source_id)]
            self.save_mapping()
            logging.info(f"[MAPPING] Entrée supprimée : page {source_id} ({lang})")
