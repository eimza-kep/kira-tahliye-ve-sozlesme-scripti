import http.server
import socketserver
import json
import sqlite3
import os
import sys
import random
from urllib.parse import urlparse

PORT = 8092
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kira_sozlesmeler.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lease_agreements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_code TEXT UNIQUE,
            landlord_name TEXT,
            landlord_id TEXT,
            tenant_name TEXT,
            tenant_id TEXT,
            tenant_phone TEXT,
            guarantor_name TEXT,
            property_type TEXT,
            property_address TEXT,
            lease_start_date TEXT,
            current_rent REAL,
            tufe_rate REAL,
            new_calculated_rent REAL,
            undertaking_sign_date TEXT,
            eviction_date TEXT,
            status TEXT DEFAULT 'Sözleşme Aktif',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

class LeaseHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_file("index.html", "text/html; charset=utf-8")
        elif path in ("/admin", "/admin.html"):
            self.send_file("admin.html", "text/html; charset=utf-8")
        elif path == "/health":
            self.send_json({"status": "ok", "app": "kira-tahliye-ve-sozlesme-scripti", "port": PORT})
        elif path == "/api/kiralar":
            self.handle_get_leases()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/kira-kaydet":
            self.handle_create_lease()
        elif path == "/api/durum-guncelle":
            self.handle_update_status()
        else:
            self.send_error(404, "Endpoint not found")

    def send_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.exists(filepath):
            self.send_error(404, f"File {filename} not found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_create_lease(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code") or f"KIRA-2026-{random.randint(1000, 9999)}"

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO lease_agreements (
                    tracking_code, landlord_name, landlord_id, tenant_name,
                    tenant_id, tenant_phone, guarantor_name, property_type,
                    property_address, lease_start_date, current_rent,
                    tufe_rate, new_calculated_rent, undertaking_sign_date,
                    eviction_date, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tracking_code,
                data.get("landlord_name", ""),
                data.get("landlord_id", ""),
                data.get("tenant_name", ""),
                data.get("tenant_id", ""),
                data.get("tenant_phone", ""),
                data.get("guarantor_name", ""),
                data.get("property_type", ""),
                data.get("property_address", ""),
                data.get("lease_start_date", ""),
                float(data.get("current_rent", 0)),
                float(data.get("tufe_rate", 0)),
                float(data.get("new_calculated_rent", 0)),
                data.get("undertaking_sign_date", ""),
                data.get("eviction_date", ""),
                data.get("status", "Sözleşme Aktif"),
                data.get("created_at", "")
            ))
            conn.commit()
            conn.close()

            self.send_json({"status": "success", "tracking_code": tracking_code})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_get_leases(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM lease_agreements ORDER BY id DESC")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            self.send_json(rows)
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_update_status(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code")
            new_status = data.get("status")

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("UPDATE lease_agreements SET status = ? WHERE tracking_code = ?", (new_status, tracking_code))
            conn.commit()
            conn.close()

            self.send_json({"status": "success", "updated": tracking_code})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", PORT))
    print(f"🚀 Kira ve Tahliye Taahhudu Portali Baslatildi: http://localhost:{port}")
    print(f"🏠 Yonetim Paneli: http://localhost:{port}/admin")
    with socketserver.TCPServer(("", port), LeaseHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu kapatildi.")
