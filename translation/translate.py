import os
import requests
import logging
from typing import Optional, List
from bs4 import BeautifulSoup, NavigableString

from config import SOURCE_LANG


class TranslationService:
    """Service de traduction basé sur l'API LibreTranslate."""

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.getenv("LIBRETRANSLATE_URL", "http://127.0.0.1:5000/translate")

        if not self.api_url:
            raise ValueError("L'URL de l'API LibreTranslate est manquante.")

        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():  # éviter de redéfinir plusieurs fois
            logging.basicConfig(level=logging.INFO)
        self.logger.info(f"Service de traduction initialisé avec l'URL : {self.api_url}")

    def _call_translation_api(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
        """Effectue un appel à l'API de traduction."""
        if not text.strip():
            return text  # Rien à traduire

        payload = {
            'q': text,
            'source': source_lang or 'auto',
            'target': target_lang,
            'format': 'text'
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            translated = result.get('translatedText')
            if not translated:
                self.logger.warning(f"Réponse API sans texte traduit pour : '{text}'")
                return text
            return translated
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur API traduction : {e}")
            return text
        except Exception as e:
            self.logger.exception(f"Erreur inattendue : {e}")
            return text

    def translate_text(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
        """Traduit du texte brut."""
        self.logger.info(f"Traduction simple -> {target_lang}")
        return self._call_translation_api(text, target_lang, source_lang)

    def translate_html(self, html: str, target_lang: str, source_lang: Optional[str] = None) -> str:
        """Traduit le texte visible dans un document HTML, en conservant les balises."""
        self.logger.info(f"Traduction HTML -> {target_lang}")
        soup = BeautifulSoup(html, 'html.parser')

        # On ne modifie que les chaînes de texte visibles (NavigableString)
        for element in soup.find_all(string=True):
            if isinstance(element, NavigableString) and element.strip():
                translated = self._call_translation_api(str(element), target_lang, source_lang)
                element.replace_with(translated)

        return str(soup)

    def batch_translate_texts(self, texts: List[str], target_lang: str, source_lang: Optional[str] = None) -> List[str]:
        """Traduit une liste de textes (un par un)."""
        self.logger.info(f"Traduction de {len(texts)} textes -> {target_lang}")
        return [self.translate_text(text, target_lang, source_lang) for text in texts]
    
    def detect_language(self, text):
        payload = {"q": text}
        headers = {"Content-Type": "application/json"}
        
        try:
            resp = requests.post(f"{self.api_url}/detect", json=payload, headers=headers)
            if resp.status_code == 200:
                detections = resp.json()
                if detections:
                    return detections[0]['language']
        except Exception as e:
                print(f"[TRANSLATE] Erreur de détection de langue : {e}")
        return SOURCE_LANG  # fallback sur langue par défaut



# Exécution directe
if __name__ == "__main__":
    service = TranslationService()

    texte = "Bonjour tout le monde!"
    print(f"Texte traduit : {service.translate_text(texte, 'en')}")

    html = "<p>Bonjour, <strong>comment ça va</strong> ?</p>"
    print(f"HTML traduit : {service.translate_html(html, 'en')}")

    lot = ["Bonjour", "Merci", "Au revoir"]
    print("Batch traduit :", service.batch_translate_texts(lot, "en"))
    