from typing import List, Optional
import logging

from translation.translate import TranslationService
from api.mapping import MappingManager
from api.books import BookStackBooksAPI
from api.chapters import BookStackChaptersAPI
from api.pages import BookStackPagesAPI


class SyncManager:
    def __init__(self):
        self.translator = TranslationService()
        self.mapping = MappingManager()
        self.book_api = BookStackBooksAPI()
        self.chapter_api = BookStackChaptersAPI()
        self.page_api = BookStackPagesAPI()
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)

        # Check if the mapping is empty and try to clean it if necessary
        if self.mapping.is_empty():
            self.logger.warning("[SYNC] Mapping vide. Tentative de nettoyage...")
            self.mapping.clean_mapping()
            self.logger.info("[SYNC] Mapping nettoyé.")

    def _ensure_translated_book(
        self,
        source_book_id: str,
        book_details: dict,
        target_lang: str
    ) -> Optional[str]:
        # Get existing mapping
        translated_book_id = self.mapping.get_book(source_book_id, target_lang)
        # Prepare translations
        translated_title = self.translator.translate_text(book_details.get('name', ''), target_lang)
        translated_description = self.translator.translate_text(
            book_details.get('description', ''), target_lang
        )

        if translated_book_id:
            # Update existing book translation
            self.logger.info(f"[SYNC] Mise à jour du livre {translated_book_id} pour {target_lang}...")
            self.book_api.update_book(
                translated_book_id,
                translated_title,
                translated_description
            )
        else:
            # Create new translated book
            new_book = self.book_api.create_book(translated_title, translated_description)
            if new_book:
                translated_book_id = new_book.get('id')
                self.mapping.set_mapped_book(source_book_id, target_lang, translated_book_id)
                self.logger.info(f"[SYNC] Livre créé pour {target_lang} : ID {translated_book_id}")
            else:
                self.logger.error(f"[SYNC] Échec création livre pour {target_lang} (source {source_book_id})")

        return translated_book_id

    def _ensure_translated_chapter(
        self,
        source_chapter_id: str,
        chapter_name: str,
        book_id: str,
        target_lang: str
    ) -> Optional[str]:
        # Get existing mapping
        translated_chapter_id = self.mapping.get_chapter(source_chapter_id, target_lang)
        # Prepare translation
        translated_name = self.translator.translate_text(chapter_name, target_lang)

        if translated_chapter_id:
            # Update existing chapter translation
            self.logger.info(f"[SYNC] Mise à jour du chapitre {translated_chapter_id} pour {target_lang}...")
            self.chapter_api.update_chapter(
                translated_chapter_id,
                translated_name
            )
        else:
            # Create new translated chapter
            chapter = self.chapter_api.create_chapter(book_id, translated_name)
            if chapter:
                translated_chapter_id = chapter.get('id')
                self.mapping.set_mapped_chapter(source_chapter_id, target_lang, translated_chapter_id)
                self.logger.info(f"[SYNC] Chapitre créé pour {target_lang} : ID {translated_chapter_id}")
            else:
                self.logger.error(f"[SYNC] Échec création chapitre pour {target_lang} (source {source_chapter_id})")

        return translated_chapter_id

    def sync_book(self, source_book_id: str, target_langs: List[str]) -> None:
        book_details = self.book_api.get_book(source_book_id)
        if not book_details:
            self.logger.warning(f"[SYNC] Livre source introuvable : {source_book_id}")
            return

        for target_lang in target_langs:
            translated_book_id = self._ensure_translated_book(
                source_book_id, book_details, target_lang
            )
            if not translated_book_id:
                continue

            # Synchronize chapters
            source_chapters = self.chapter_api.get_chapters(source_book_id)
            for source_chapter in source_chapters:
                translated_chapter_id = self._ensure_translated_chapter(
                    source_chapter['id'],
                    source_chapter.get('name', ''),
                    translated_book_id,
                    target_lang
                )
                if not translated_chapter_id:
                    continue

                # Synchronize pages
                source_pages = self.page_api.get_pages(source_chapter['id'])
                for source_page in source_pages:
                    self.sync_page(source_page['id'], [target_lang])

    def sync_page(self, source_page_id: str, target_langs: List[str]) -> None:
        source_page = self.page_api.get_page(source_page_id)
        if not source_page:
            self.logger.warning(f"[SYNC] Page source introuvable : {source_page_id}")
            return

        page_name = source_page.get('name', '')
        html_content = source_page.get('html', '')
        source_book_id = str(source_page.get('book_id'))
        source_chapter_id = source_page.get('chapter_id')

        source_lang = self.translator.detect_language(page_name or html_content)
        if not source_lang:
            self.logger.warning(f"[SYNC] Langue source indétectable pour la page : {source_page_id}")
            return

        for target_lang in target_langs:
            if target_lang == source_lang:
                continue

            existing_page_id = self.mapping.get_page(source_page_id, target_lang)
            translated_name = self.translator.translate_text(page_name, target_lang, source_lang)
            translated_html = self.translator.translate_html(html_content, target_lang, source_lang)

            if existing_page_id:
                # Update existing page
                self.logger.info(f"[SYNC] Mise à jour page {existing_page_id} pour {target_lang}...")
                self.page_api.update_page(
                    existing_page_id,
                    translated_name,
                    translated_html,
                    book_id=self.mapping.get_book(source_book_id, target_lang),
                    chapter_id=self.mapping.get_chapter(source_chapter_id, target_lang) if source_chapter_id else None
                )
                continue

            # Create new translated page
            translated_book_id = self._ensure_translated_book(
                source_book_id,
                self.book_api.get_book(source_book_id) or {},
                target_lang
            )
            translated_chapter_id = None
            if source_chapter_id:
                translated_chapter_id = self._ensure_translated_chapter(
                    source_chapter_id,
                    self.chapter_api.get_chapter(source_chapter_id).get('name', ''),
                    translated_book_id,
                    target_lang
                )

            created = self.page_api.create_page(
                book_id=translated_book_id,
                chapter_id=translated_chapter_id,
                name=translated_name,
                html=translated_html,
                lang=target_lang,
                source_page_id=source_page_id
            )

            if created:
                new_id = created.get('id')
                self.mapping.set_mapped_page(source_page_id, target_lang, new_id)
                self.logger.info(f"[SYNC] Page créée pour {target_lang} : ID {new_id}")
            else:
                self.logger.error(f"[SYNC] Échec création page pour {target_lang} (source {source_page_id})")

    def clean_mapping(self, valid_book_ids=None, valid_chapter_ids=None, valid_page_ids=None):
        """
        Nettoie manuellement les mappings si besoin via appel direct.
        """
        self.mapping.clean_mapping(
            valid_book_ids or set(),
            valid_chapter_ids or set(),
            valid_page_ids or set()
        )
        self.logger.info("[SYNC] Nettoyage du mapping terminé.")
