from dotenv import load_dotenv
load_dotenv()
import os

# === BookStack API Configuration ===
BOOKSTACK_API_BASE = os.getenv("BOOKSTACK_API_BASE", "http://localhost:8080/api")
BOOKSTACK_TOKEN_ID = os.getenv("BOOKSTACK_TOKEN_ID")
BOOKSTACK_TOKEN_SECRET = os.getenv("BOOKSTACK_TOKEN_SECRET")

BOOKSTACK_HEADERS = {
    "Authorization": f"Token {BOOKSTACK_TOKEN_ID}:{BOOKSTACK_TOKEN_SECRET}",
    "Content-Type": "application/json"
}

# === Translation Configuration ===
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL")
LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY")

# Langues par défaut
SOURCE_LANG = os.getenv("SOURCE_LANG", "fr")
TARGET_LANGS = os.getenv("TARGET_LANG", "en,es,de").split(",")

# === Directory Configuration ===
TRANSLATED_DIR = os.getenv("TRANSLATED_DIR", os.path.join("data", "translated"))
BOOKSTACK_DIR = os.getenv("BOOKSTACK_DIR", os.path.join("data", "bookstack"))
DB_DIR = os.getenv("DB_DIR", "db")
MAPPING_FILE = os.path.join(DB_DIR, "mapping.json")
MAPPING_FILE_BACKUP = os.path.join(DB_DIR, "mapping_backup.json")
MAPPING_FILE_TEMP = os.path.join(DB_DIR, "mapping_temp.json")