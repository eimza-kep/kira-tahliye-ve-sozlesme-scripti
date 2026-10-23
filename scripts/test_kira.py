import unittest
import os
import sys
import sqlite3

# Ensure parent directory and scripts directory are in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import server
from tufe_kira_calculator import get_tufe_rate_for_date, calculate_tbk_rent_increase
from kira_eimza_engine import verify_eviction_undertaking_legal_validity, verify_digital_signature_document

class TestLeaseSystem(unittest.TestCase):
    def setUp(self):
        server.init_db()
        self.conn = sqlite3.connect(server.DB_FILE)
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("DELETE FROM lease_agreements WHERE tracking_code LIKE 'KIRA-TEST%'")
        self.conn.commit()

    def tearDown(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM lease_agreements WHERE tracking_code LIKE 'KIRA-TEST%'")
        self.conn.commit()
        self.conn.close()

    def test_database_table_exists(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lease_agreements'")
        row = cur.fetchone()
        self.assertIsNotNone(row, "lease_agreements tablosu oluşturulmuş olmalıdır.")

    def test_table_has_eimza_and_tufe_columns(self):
        cur = self.conn.cursor()
        cur.execute("PRAGMA table_info(lease_agreements)")
        columns = [row["name"] for row in cur.fetchall()]
        self.assertIn("eimza_verified", columns)
        self.assertIn("eimza_signer_tckn", columns)
        self.assertIn("eimza_timestamp", columns)
        self.assertIn("eimza_cert_issuer", columns)
        self.assertIn("undertaking_legal_status", columns)
        self.assertIn("pdf_doc_base64", columns)

    def test_lease_insert_and_retrieve_with_eimza(self):
        cur = self.conn.cursor()
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
            "KIRA-TEST-001",
            "Ahmet Mal Sahibi",
            "11122233344",
            "Mehmet Kiracı",
            "55566677788",
            "05329998877",
            "Ali Kefil",
            "Konut (Daire / Ev)",
            "Beşiktaş, İstanbul",
            "2025-10-01",
            20000.0,
            38.64,
            27728.0,
            "2025-10-15",
            "2026-10-01",
            "Sözleşme Aktif",
            "2026-09-20T10:00:00Z",
            1,
            "55566677788",
            "2026-10-23T05:00:00Z",
            "TÜRKTRUST Bilgi İletişim ve Bilişim Güvenliği Hizmetleri A.Ş.",
            "HUKUKEN_GECERLI",
            "data:application/pdf;base64,JVBERi0xLjQKJUZha2VQREZDZ=="
        ))
        self.conn.commit()

        cur.execute("SELECT * FROM lease_agreements WHERE tracking_code = 'KIRA-TEST-001'")
        record = cur.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record["tenant_name"], "Mehmet Kiracı")
        self.assertEqual(record["new_calculated_rent"], 27728.0)
        self.assertEqual(record["eimza_verified"], 1)
        self.assertEqual(record["undertaking_legal_status"], "HUKUKEN_GECERLI")
        self.assertIn("TÜRKTRUST", record["eimza_cert_issuer"])

    def test_tufe_rate_lookup(self):
        res = get_tufe_rate_for_date("2026-10-15")
        self.assertEqual(res["period"], "2026-10")
        self.assertEqual(res["rate"], 38.64)
        self.assertTrue(res["is_legal_cap"])
        self.assertIn("TBK Madde 344/2", res["legal_basis"])

        res_2025 = get_tufe_rate_for_date("2025-12-01")
        self.assertEqual(res_2025["rate"], 61.20)

    def test_calculate_tbk_rent_increase(self):
        calc = calculate_tbk_rent_increase(20000.0, "2026-10-01")
        self.assertEqual(calc["current_rent"], 20000.0)
        self.assertEqual(calc["tufe_rate"], 38.64)
        self.assertEqual(calc["increase_amount"], 7728.0)
        self.assertEqual(calc["new_rent"], 27728.0)
        self.assertTrue(calc["is_tbk_compliant"])
        self.assertIsNone(calc["warning"])

        # Test exceeding rate
        calc_warn = calculate_tbk_rent_increase(20000.0, "2026-10-01", custom_rate=50.0)
        self.assertFalse(calc_warn["is_tbk_compliant"])
        self.assertIsNotNone(calc_warn["warning"])
        self.assertEqual(calc_warn["legal_max_rent"], 27728.0)

    def test_eviction_undertaking_legal_validity(self):
        # 1. Valid: Sign date after lease start date
        valid_res = verify_eviction_undertaking_legal_validity("2025-10-01", "2025-10-15", "2026-10-01")
        self.assertTrue(valid_res["is_valid"])
        self.assertEqual(valid_res["status"], "HUKUKEN_GECERLI")
        self.assertEqual(valid_res["days_after_lease"], 14)

        # 2. Risky: Same day
        same_day_res = verify_eviction_undertaking_legal_validity("2025-10-01", "2025-10-01", "2026-10-01")
        self.assertFalse(same_day_res["is_valid"])
        self.assertEqual(same_day_res["status"], "RISKLI_AYNI_GUN")

        # 3. Invalid: Sign date before lease
        before_res = verify_eviction_undertaking_legal_validity("2025-10-01", "2025-09-20", "2026-10-01")
        self.assertFalse(before_res["is_valid"])
        self.assertEqual(before_res["status"], "GECERSIZ_ONCE_TANZIM")

        # 4. Invalid eviction date
        bad_evict_res = verify_eviction_undertaking_legal_validity("2025-10-01", "2025-10-15", "2025-10-10")
        self.assertFalse(bad_evict_res["is_valid"])
        self.assertEqual(bad_evict_res["status"], "GECERSIZ_TAHLIYE_TARIHI")

    def test_digital_signature_verification(self):
        dummy_b64 = "JVBERi0xLjQKJUZha2VFSU1aQURvY3VtZW50=="
        res = verify_digital_signature_document(dummy_b64, "55566677788", "Mehmet Kiracı")
        self.assertTrue(res["valid"])
        self.assertTrue(res["is_eimza_verified"])
        self.assertEqual(res["signer_tckn"], "55566677788")
        self.assertEqual(res["signer_name"], "Mehmet Kiracı")
        self.assertIn("PAdES-LTV", res["signature_standard"])
        self.assertIsNotNone(res["sha256_digest"])

    def test_files_exist(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "index.html")), "index.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "admin.html")), "admin.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "server.py")), "server.py bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "api.php")), "api.php bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "scripts", "tufe_kira_calculator.py")), "tufe_kira_calculator.py bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "scripts", "kira_eimza_engine.py")), "kira_eimza_engine.py bulunamadı")

if __name__ == "__main__":
    unittest.main()
