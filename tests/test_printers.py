"""Isolated printer API tests. No connection to the application's existing DB.

.venv/Scripts/python -m unittest discover -s tests -p test_printers.py -v
PRINTER_TEST_MYSQL=1 additionally tests real MySQL row locks using .env login,
creating and dropping a uniquely named printer_test_* database only.
"""
import os
# Read local .env when present without printing values. Synthetic defaults only
# satisfy application imports for SQLite runs on machines without a .env file.
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("DB_PASSWORD", "printer-tests-unused")
os.environ.setdefault("SECRET_KEY", "isolated-printer-test-signing-key")
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.api.v1 import printers as api
from app.core.database import Base, get_db
from app.core.dependencies import require_admin
from app.core.limiter import limiter
from app.models.printer_booking import PRINTER_TABLES, PrinterConfig, PrinterBooking, PrinterTeam, Printer, initialize_printers


class PrinterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.engine = create_engine("sqlite:///" + str(Path(cls.tmp.name) / "printers.sqlite"), connect_args={"check_same_thread": False, "timeout": 20})
        cls.Session = sessionmaker(bind=cls.engine, expire_on_commit=False)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        cls.tmp.cleanup()

    def setUp(self):
        Base.metadata.drop_all(self.engine, tables=list(reversed(PRINTER_TABLES)))
        Base.metadata.create_all(self.engine, tables=PRINTER_TABLES)
        with self.Session() as db:
            initialize_printers(db)
            cfg = db.get(PrinterConfig, 1)
            cfg.registration_code_hash = api.get_password_hash("invite-test-2026")
            cfg.registration_enabled = True
            for i in (1, 2):
                db.add(PrinterTeam(id=i, module_key="bambu_cup", team_name=f"Team {i}", captain_name=f"Captain {i}", captain_student_id=str(i), captain_phone_hash=api.get_password_hash("13800000000"), access_code_hash=api.get_password_hash("private-team-code")))
            db.commit()
        self.app = FastAPI()
        self.app.state.limiter = limiter
        limiter.enabled = False
        self.app.include_router(api.router)
        def db_dep():
            with self.Session() as db:
                yield db
        self.app.dependency_overrides[get_db] = db_dep
        self.client = TestClient(self.app)
        self.token = api.create_access_token({"sub": "0", "scope": "printer_team", "printer_team_id": 1})
        self.headers = {"Authorization": "Bearer " + self.token}
        self.future = api.now().replace(microsecond=0) + timedelta(days=2)

    def post(self, path, data=None, headers=None):
        return self.client.post("/api/v1/printers" + path, json=data, headers=headers or self.headers)

    def reserve(self, start=None, end=None, printer_id=1):
        start = start or self.future
        end = end or start + timedelta(hours=1)
        return self.post("/bookings", {"printer_id": printer_id, "start_time": start.isoformat(), "end_time": end.isoformat(), "purpose": "模型"})

    def admin(self):
        self.app.dependency_overrides[require_admin] = lambda: SimpleNamespace(id=99)

    def test_seed_idempotent_config_and_private_data(self):
        with self.Session() as db:
            initialize_printers(db)
            self.assertEqual(db.query(Printer).count(), 3)
        cfg = self.client.get("/api/v1/printers/config").json()["data"]
        self.assertEqual(cfg["timezone"], "Asia/Shanghai")
        self.assertFalse(cfg["opening_hours_enabled"])
        self.reserve()
        rows = self.client.get("/api/v1/printers/bookings", params={"date": self.future.date().isoformat()}).json()["data"]
        self.assertEqual(len(rows), 1)
        self.assertNotIn("captain_student_id", rows[0])
        self.assertNotIn("purpose", rows[0])
        self.assertTrue(rows[0]["start_time"].endswith("+08:00"))

    def test_overlap_boundaries_cross_midnight_and_machines(self):
        self.assertEqual(self.reserve().status_code, 200)
        self.assertEqual(self.reserve().status_code, 409)
        self.assertEqual(self.reserve(self.future - timedelta(minutes=10), self.future + timedelta(minutes=10)).status_code, 409)
        self.assertEqual(self.reserve(self.future + timedelta(hours=1)).status_code, 200)
        self.assertEqual(self.reserve(printer_id=2).status_code, 200)
        midnight = self.future.replace(hour=23, minute=0)
        self.assertEqual(self.reserve(midnight, midnight + timedelta(hours=4), 3).status_code, 200)
        self.assertEqual(self.reserve(midnight + timedelta(hours=2), midnight + timedelta(hours=5), 3).status_code, 409)

    def test_input_open_hours_and_timezone(self):
        self.assertEqual(self.reserve(self.future, self.future).status_code, 400)
        self.assertEqual(self.reserve(api.now() - timedelta(hours=1)).status_code, 400)
        self.admin()
        day = self.future.replace(hour=9, minute=0)
        response = self.client.put("/api/v1/printers/admin/config", json={"opening_hours_enabled": True, "opening_hours": [{"weekday": day.weekday(), "start": "09:00", "end": "18:00"}]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.reserve(day, day + timedelta(days=1)).status_code, 200)
        self.assertEqual(self.reserve(day.replace(hour=18), day.replace(hour=19), 2).status_code, 400)
        self.assertEqual(self.reserve(day.replace(hour=8), day.replace(hour=9), 2).status_code, 400)
        # UTC 01:00 is local 09:00.
        r = self.post("/bookings", {"printer_id": 2, "start_time": day.strftime("%Y-%m-%dT01:00:00Z"), "end_time": day.strftime("%Y-%m-%dT02:00:00Z")})
        self.assertEqual(r.status_code, 200)

    def test_registration_identification_password_unicode_and_scope(self):
        data = {"captain_student_id": "new1", "captain_phone": "13800000000", "access_code": "中文口令测试" * 8, "team_name": "新队伍", "captain_name": "队长", "registration_code": "invite-test-2026"}
        r = self.post("/teams", data)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(self.post("/teams", data).status_code, 409)
        auth = {k: data[k] for k in ("captain_student_id", "captain_phone", "access_code")}
        self.assertEqual(self.post("/identify", auth).status_code, 200)
        auth["access_code"] += "错"
        self.assertEqual(self.post("/identify", auth).status_code, 401)
        auth["access_code"] = data["access_code"]
        auth["captain_phone"] = "13900000000"
        self.assertEqual(self.post("/identify", auth).status_code, 401)
        self.assertEqual(self.client.get("/api/v1/printers/my-bookings").status_code, 401)
        user_token = api.create_access_token({"sub": "1"})
        self.assertEqual(self.client.get("/api/v1/printers/my-bookings", headers={"Authorization": "Bearer " + user_token}).status_code, 401)
        self.assertEqual(self.client.get("/api/v1/printers/admin/config", headers=self.headers).status_code, 401)
        with self.Session() as db:
            t = db.query(PrinterTeam).filter_by(captain_student_id="new1").one()
            self.assertNotIn(data["access_code"], t.access_code_hash)
            self.assertNotIn(data["captain_phone"], t.captain_phone_hash)

    def test_cancel_authorization_and_reuse(self):
        b = self.reserve().json()["data"]
        other = {"Authorization": "Bearer " + api.create_access_token({"sub": "0", "scope": "printer_team", "printer_team_id": 2})}
        self.assertEqual(self.post(f'/bookings/{b["id"]}/cancel', headers=other).status_code, 403)
        self.assertEqual(self.post(f'/bookings/{b["id"]}/cancel').status_code, 200)
        self.assertEqual(self.reserve().status_code, 200)
        self.assertEqual(self.post(f'/bookings/{b["id"]}/check-in').status_code, 409)

    def seed_use(self):
        t = api.now().replace(microsecond=0)
        with self.Session() as db:
            prev = PrinterBooking(printer_id=1, team_id=2, team_name="Previous actual team", captain_name="Previous captain", captain_student_id="2", start_time=t-timedelta(hours=4), end_time=t-timedelta(hours=3), status="completed", checked_in_at=t-timedelta(hours=4), checked_out_at=t-timedelta(hours=3))
            unused = PrinterBooking(printer_id=1, team_id=2, team_name="Never checked in", captain_name="Unused", captain_student_id="2", start_time=t-timedelta(hours=2), end_time=t-timedelta(hours=1), status="reserved")
            current = PrinterBooking(printer_id=1, team_id=1, team_name="Team 1", captain_name="Captain 1", captain_student_id="1", start_time=t-timedelta(minutes=1), end_time=t+timedelta(minutes=30), status="reserved")
            future = PrinterBooking(printer_id=1, team_id=2, team_name="Future team", captain_name="Future", captain_student_id="2", start_time=t+timedelta(hours=1), end_time=t+timedelta(hours=2), status="reserved")
            db.add_all([prev, unused, current, future])
            db.commit()
            return prev.id, current.id

    def test_actual_handover_incident_snapshot_maintenance(self):
        prev, current = self.seed_use()
        r = self.post(f"/bookings/{current}/check-in")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["data"]["previous_booking_id"], prev)
        r = self.post(f"/bookings/{current}/incidents", {"description": "接机检查发现喷头堵塞"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["responsible_team_name"], "Previous actual team")
        self.assertEqual(self.reserve().status_code, 409)
        self.admin()
        self.assertEqual(self.client.put("/api/v1/printers/admin/printers/1", json={"status": "available"}).status_code, 409)
        incident_id = r.json()["data"]["id"]
        self.assertEqual(self.post(f"/admin/incidents/{incident_id}/resolve", {"resolution": "已检查并清理喷头"}).status_code, 200)
        self.assertEqual(self.client.put("/api/v1/printers/admin/printers/1", json={"status": "available"}).status_code, 200)
        self.assertEqual(self.post(f"/bookings/{current}/check-out").status_code, 200)
        self.assertEqual(self.post(f"/bookings/{current}/check-out").status_code, 409)
        records = self.client.get("/api/v1/printers/admin/incidents").json()["data"]
        self.assertEqual(records[0]["previous_booking_id"], prev)

    def test_report_before_check_in_and_no_previous(self):
        prev, current = self.seed_use()
        r = self.post(f"/bookings/{current}/incidents", {"description": "接机前发现平台损坏"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["previous_booking_id"], prev)
        with self.Session() as db:
            db.query(PrinterBooking).filter(PrinterBooking.id == prev).update({"checked_in_at": None})
            db.commit()
        r = self.post(f"/bookings/{current}/incidents", {"description": "再次检查发现耗材缺失"})
        self.assertIsNone(r.json()["data"]["previous_booking_id"])

    def test_simultaneous_use_prevented_and_early_checkin(self):
        prev, current = self.seed_use()
        with self.Session() as db:
            db.get(PrinterBooking, prev).status = "in_use"
            db.commit()
        self.assertEqual(self.post(f"/bookings/{current}/check-in").status_code, 409)
        b = self.reserve(printer_id=2).json()["data"]
        self.assertEqual(self.post(f'/bookings/{b["id"]}/check-in').status_code, 409)

    def test_concurrent_same_machine(self):
        gate = Barrier(2)
        def attempt(_):
            gate.wait()
            return self.reserve().status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, [1, 2]))
        self.assertEqual(sorted(results), [200, 409])


@unittest.skipUnless(os.environ.get("PRINTER_TEST_MYSQL") == "1", "opt-in isolated MySQL test")
class MySQLPrinterTests(PrinterTests):
    @classmethod
    def setUpClass(cls):
        from app.core.config import Settings
        from sqlalchemy.engine import URL
        import uuid
        cfg = Settings(_env_file=".env")
        cls.db_name = "printer_test_" + uuid.uuid4().hex[:12]
        url = URL.create("mysql+pymysql", username=cfg.DB_USER, password=cfg.DB_PASSWORD, host=cfg.DB_HOST, port=cfg.DB_PORT)
        cls.root_engine = create_engine(url)
        with cls.root_engine.begin() as conn:
            conn.execute(text(f"CREATE DATABASE `{cls.db_name}` CHARACTER SET utf8mb4"))
        cls.engine = create_engine(url.set(database=cls.db_name), pool_size=5)
        cls.Session = sessionmaker(bind=cls.engine, expire_on_commit=False)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        with cls.root_engine.begin() as conn:
            conn.execute(text(f"DROP DATABASE `{cls.db_name}`"))
        cls.root_engine.dispose()


if __name__ == "__main__":
    unittest.main()
