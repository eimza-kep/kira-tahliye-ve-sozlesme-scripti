import http.server
import socketserver
import json
import sqlite3
import os
import sys
import random
from urllib.parse import urlparse, parse_qs

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
try:
    from tufe_kira_calculator import get_tufe_rate_for_date, calculate_tbk_rent_increase
    from kira_eimza_engine import verify_eviction_undertaking_legal_validity, verify_digital_signature_document
except ImportError:
    get_tufe_rate_for_date = None
    calculate_tbk_rent_increase = None
    verify_eviction_undertaking_legal_validity = None
    verify_digital_signature_document = None

PORT = int(os.environ.get("PORT", 8092))
DB_FILE = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "kira_sozlesmeler.db"))

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

    # Dynamic schema migrations for TÜİK TÜFE and E-İmza (Issue #1 and #2)
    cur.execute("PRAGMA table_info(lease_agreements)")
    existing_cols = [row[1] for row in cur.fetchall()]

    new_columns = [
        ("eimza_verified", "INTEGER DEFAULT 0"),
        ("eimza_signer_tckn", "TEXT DEFAULT ''"),
        ("eimza_timestamp", "TEXT DEFAULT ''"),
        ("eimza_cert_issuer", "TEXT DEFAULT ''"),
        ("undertaking_legal_status", "TEXT DEFAULT 'HUKUKEN_GECERLI'"),
        ("pdf_doc_base64", "TEXT DEFAULT ''")
    ]

    for col_name, col_type in new_columns:
        if col_name not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE lease_agreements ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

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
        elif path == "/api/tufe-orani":
            self.handle_get_tufe_rate(parsed)
        elif path == "/api/taahhut-gecerlilik":
            self.handle_check_undertaking_validity(parsed)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/kira-kaydet":
            self.handle_create_lease()
        elif path == "/api/durum-guncelle":
            self.handle_update_status()
        elif path == "/api/kira-hesapla":
            self.handle_calculate_rent()
        elif path == "/api/eimza-dogrula":
            self.handle_verify_eimza()
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

    def handle_get_tufe_rate(self, parsed):
        qs = parse_qs(parsed.query)
        tarih = qs.get("tarih", [""])[0].strip() or qs.get("date", [""])[0].strip()
        if get_tufe_rate_for_date:
            res = get_tufe_rate_for_date(tarih)
            self.send_json(res)
        else:
            self.send_json({"period": "2026-10", "rate": 38.64, "is_legal_cap": True})

    def handle_check_undertaking_validity(self, parsed):
        qs = parse_qs(parsed.query)
        lease_date = qs.get("lease_date", [""])[0]
        sign_date = qs.get("sign_date", [""])[0]
        evict_date = qs.get("evict_date", [""])[0]

        if verify_eviction_undertaking_legal_validity:
            res = verify_eviction_undertaking_legal_validity(lease_date, sign_date, evict_date)
            self.send_json(res)
        else:
            self.send_json({"is_valid": True, "status": "HUKUKEN_GECERLI"})

    def handle_calculate_rent(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            cur_rent = float(data.get("current_rent", 0))
            renewal_date = data.get("renewal_date") or data.get("lease_start_date") or ""
            custom_rate = data.get("custom_rate")

            if calculate_tbk_rent_increase:
                res = calculate_tbk_rent_increase(cur_rent, renewal_date, custom_rate)
                self.send_json(res)
            else:
                rate = 38.64
                inc = cur_rent * (rate / 100.0)
                self.send_json({"current_rent": cur_rent, "tufe_rate": rate, "new_rent": cur_rent + inc})
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_verify_eimza(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            b64 = data.get("pdf_base64", "")
            tckn = data.get("signer_tckn", "")
            name = data.get("signer_name", "")

            if verify_digital_signature_document:
                res = verify_digital_signature_document(b64, tckn, name)
                self.send_json(res)
            else:
                self.send_json({"valid": True, "is_eimza_verified": True})
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_create_lease(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code") or f"KIRA-2026-{random.randint(1000, 9999)}"

            eimza_ver = 1 if data.get("eimza_verified") else 0
            signer_tc = data.get("eimza_signer_tckn", "")
            eimza_ts = data.get("eimza_timestamp", "")
            eimza_cert = data.get("eimza_cert_issuer", "")
            legal_status = data.get("undertaking_legal_status", "HUKUKEN_GECERLI")
            pdf_b64 = data.get("pdf_doc_base64", "")

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO lease_agreements (
                    tracking_code, landlord_name, landlord_id, tenant_name,
                    tenant_id, tenant_phone, guarantor_name, property_type,
                    property_address, lease_start_date, current_rent,
                    tufe_rate, new_calculated_rent, undertaking_sign_date,
                    eviction_date, status, created_at,
                    eimza_verified, eimza_signer_tckn, eimza_timestamp,
                    eimza_cert_issuer, undertaking_legal_status, pdf_doc_base64
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                data.get("created_at", ""),
                eimza_ver,
                signer_tc,
                eimza_ts,
                eimza_cert,
                legal_status,
                pdf_b64
            ))
            conn.commit()
            conn.close()

            self.send_json({
                "status": "success",
                "tracking_code": tracking_code,
                "eimza_verified": bool(eimza_ver),
                "undertaking_legal_status": legal_status
            })
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
