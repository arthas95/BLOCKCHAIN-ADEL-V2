from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # ---------------------------------------------------------
        # 1) PAGE PRINCIPALE : serpent HTML
        # ---------------------------------------------------------
        if self.path == "/" or self.path == "/index.html":
            try:
                with open("index.html", "r", encoding="utf-8") as f:
                    html = f.read().encode()

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(html)

            except FileNotFoundError:
                self.send_error(500, "index.html introuvable")
            return

        # ---------------------------------------------------------
        # 2) ENDPOINT JSON : /chain
        # ---------------------------------------------------------
        if self.path == "/chain":
            try:
                with open("transactions.json", "r", encoding="utf-8") as f:
                    data = json.load(f)

                response = json.dumps(data).encode()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(response)

            except FileNotFoundError:
                self.send_error(500, "transactions.json introuvable")
            return

        # ---------------------------------------------------------
        # 3) TOUS LES AUTRES ENDPOINTS → erreur
        # ---------------------------------------------------------
        self.send_error(404, "Page non trouvée")


# ---------------------------------------------------------
# LANCEMENT DU SERVEUR
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🌐 Serveur web lancé sur http://localhost:8000")
    print("👉 /        → Page du serpent")
    print("👉 /chain   → JSON de la blockchain")
    server = HTTPServer(("localhost", 8000), MyHandler)
    server.serve_forever()
