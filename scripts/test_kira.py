import unittest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

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

    def test_lease_insert_and_retrieve(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO lease_agreements (
                tracking_code, landlord_name, landlord_id, tenant_name,
                tenant_id, tenant_phone, guarantor_name, property_type,
                property_address, lease_start_date, current_rent,
                tufe_rate, new_calculated_rent, undertaking_sign_date,
                eviction_date, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            60.0,
            32000.0,
            "2025-10-15",
            "2026-10-01",
            "Sözleşme Aktif",
            "2026-09-20T10:00:00Z"
        ))
        self.conn.commit()

        cur.execute("SELECT * FROM lease_agreements WHERE tracking_code = 'KIRA-TEST-001'")
        record = cur.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record["tenant_name"], "Mehmet Kiracı")
        self.assertEqual(record["new_calculated_rent"], 32000.0)

    def test_lease_status_update(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO lease_agreements (tracking_code, tenant_name, status)
            VALUES (?, ?, ?)
        """, ("KIRA-TEST-002", "Ayşe Kiracı", "Sözleşme Aktif"))
        self.conn.commit()

        cur.execute("""
            UPDATE lease_agreements
            SET status = 'Tahliye Edildi'
            WHERE tracking_code = 'KIRA-TEST-002'
        """)
        self.conn.commit()

        cur.execute("SELECT status FROM lease_agreements WHERE tracking_code = 'KIRA-TEST-002'")
        row = cur.fetchone()
        self.assertEqual(row["status"], "Tahliye Edildi")

    def test_files_exist(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "index.html")), "index.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "admin.html")), "admin.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "api.php")), "api.php bulunamadı")

if __name__ == "__main__":
    unittest.main()
