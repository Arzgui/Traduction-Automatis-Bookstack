from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import sys
import os

# Add directory to path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import TARGET_LANGS

# Set up logging
logging.basicConfig(level=logging.INFO)

class WebhookHandler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            json_data = json.loads(post_data.decode('utf-8'))

            print("Requête webhook reçue :", json_data)

            event_type = json_data.get("event")

            if event_type == "chapter_create":
                chapter_id = json_data.get("chapter_id")
                if not chapter_id:
                    try:
                        return self._send_json(400, {"error": "Missing 'chapter_id'"})
                    except ConnectionAbortedError:
                        self.log_error("Client déconnecté lors du renvoi de l'erreur 400.")
                        return

                
                logging.info(f"[WEBHOOK] Nouveau chapitre : {chapter_id}")
                

            elif event_type == "page_update":
                related = json_data.get("related_item", {})
                page_id = related.get("id")
                if not page_id:
                    try:
                        return self._send_json(400, {"error": "Missing 'page_id'"})
                    except ConnectionAbortedError:
                        self.log_error("Client déconnecté lors du renvoi de l'erreur 400.")
                        return

                logging.info(f"[WEBHOOK] Mise à jour de la page : {page_id}")
                from translation.sync import SyncManager
                sync = SyncManager()
                sync.sync_page(page_id, TARGET_LANGS)

            else:
                logging.warning(f"[WEBHOOK] Événement non géré : {event_type}")
                try:
                    return self._send_json(400, {"error": "Unsupported event type"})
                except ConnectionAbortedError:
                    self.log_error("Client déconnecté lors du renvoi de l'erreur 400.")
                    return

            return self._send_json(200, {"status": "ok"})

        except Exception as e:
            logging.exception("Erreur interne lors du traitement de la requête")
            try:
                return self._send_json(500, {"error": "Internal server error"})
            except ConnectionAbortedError:
                self.log_error("Client déconnecté avant envoi de l'erreur 500.")
                return
    def _send_json(self, code, data):
        try:
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            payload = json.dumps(data).encode('utf-8')
            self.wfile.write(payload)
        except ConnectionAbortedError:
            logging.error("Échec de l'envoi de la réponse JSON : connexion interrompue")
            return

            

def run(port=5050):
    logging.info(f"Server running at http://0.0.0.0:{port}/webhook")
    HTTPServer(("0.0.0.0", port), WebhookHandler).serve_forever()


if __name__ == "__main__":
    run()
    # run(5050)  # Uncomment to run the server directly for testing purposes
    print("Server started on port 5050")