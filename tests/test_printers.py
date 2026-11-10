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
from app.models.printer_booking import PRINTER_TABLES, PrinterConfig, PrinterBooking, PrinterIncident, Printer, initialize_printers
from app.models.team import Team, TeamStatus
from app.models.team_member import TeamMember
from app.models.competition_event import CompetitionEvent


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
        if self.engine.dialect.name == "sqlite":
            with self.engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys=OFF"))
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        with self.Session() as db:
            initialize_printers(db)
            db.add(CompetitionEvent(id=1, name="拓竹杯2026", cup_type="wireless", module_key="bambu_cup", is_current=1))
            db.add(CompetitionEvent(id=2, name="无线杯", cup_type="wireless", module_key="wireless_cup", is_current=1))
            for i in (1, 2):
                db.add(Team(id=i, module_key="bambu_cup", team_name=f"Team {i}", captain_name=f"Captain {i}", captain_student_id=str(i), captain_phone="13800000000", status=TeamStatus.SUBMITTED))
            db.add(Team(id=3, module_key="wireless_cup", team_name="Other event", captain_name="Other", captain_student_id="3", captain_phone="13800000000"))
            db.add(TeamMember(team_id=1, name="Member", student_id="member1", phone="13800000000"))
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
        self.token = api.create_access_token({"sub": "0", "scope": "printer_team", "competition_team_id": 1, "module_key": "bambu_cup", "captain_student_id": "1"})
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

    def test_schedule_captain_phone_and_admin_contact(self):
        self.reserve()
        path = "/api/v1/printers/bookings?date=" + self.future.date().isoformat()
        self.assertEqual(self.client.get(path).json()["data"][0]["captain_phone"], "13800000000")
        with self.Session() as db:
            db.get(Team, 1).captain_phone = "13900000000"
            db.commit()
        self.assertEqual(self.client.get(path).json()["data"][0]["captain_phone"], "13900000000")
        # Contacts are deliberately public for handover; no other captain identity is exposed.
        self.assertNotIn("captain_student_id", self.client.get(path).json()["data"][0])
        self.assertEqual(self.client.put("/api/v1/printers/admin/config", json={"admin_contact": "不能修改"}, headers=self.headers).status_code, 401)
        self.admin()
        response = self.client.put("/api/v1/printers/admin/config", json={"admin_contact": "  管理员 王老师：020-12345678 / 微信 office-admin  "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/v1/printers/config").json()["data"]["admin_contact"], "管理员 王老师：020-12345678 / 微信 office-admin")
        # Other config edits preserve contacts when omitted; empty input explicitly clears.
        self.client.put("/api/v1/printers/admin/config", json={"opening_hours_enabled": False})
        self.assertTrue(self.client.get("/api/v1/printers/config").json()["data"]["admin_contact"])
        self.assertEqual(self.client.put("/api/v1/printers/admin/config", json={"admin_contact": "x" * 301}).status_code, 422)
        self.client.put("/api/v1/printers/admin/config", json={"admin_contact": ""})
        self.assertEqual(self.client.get("/api/v1/printers/config").json()["data"]["admin_contact"], "")

    def test_contact_column_incremental_migration(self):
        from scripts.init_printers import migrate_printers
        with self.engine.begin() as conn:
            conn.execute(text("ALTER TABLE printer_configs DROP COLUMN admin_contact"))
        migrate_printers(self.engine)
        migrate_printers(self.engine)
        with self.Session() as db:
            self.assertEqual(db.get(PrinterConfig, 1).admin_contact, "")
            db.get(PrinterConfig, 1).admin_contact = "联系办公室管理员"
            db.commit()
        migrate_printers(self.engine)
        self.assertEqual(self.client.get("/api/v1/printers/config").json()["data"]["admin_contact"], "联系办公室管理员")

    def test_schedule_status_boundaries_public_private_identity_and_admin(self):
        booking = self.reserve().json()["data"]
        self.admin()
        start = self.future
        end = start + timedelta(hours=1)
        cases = [(start - timedelta(microseconds=1), "reserved"),
                 (start, "in_use"), (end - timedelta(microseconds=1), "in_use"),
                 (end, "completed"), (end + timedelta(hours=1), "completed")]
        for current, expected in cases:
            with self.subTest(current=current, expected=expected):
                for path, headers in [
                    ("/bookings?date=" + start.date().isoformat(), None),
                    ("/my-bookings", self.headers),
                    ("/admin/bookings?date=" + start.date().isoformat(), None),
                ]:
                    with patch.object(api, "now", return_value=current) as clock:
                        response = self.client.get("/api/v1/printers" + path, headers=headers)
                    self.assertEqual(response.status_code, 200, response.text)
                    rows = response.json()["data"]
                    row = next(b for b in rows if b["id"] == booking["id"])
                    self.assertEqual(row["status"], expected)
                    self.assertEqual(row["usage_status"], "reserved")
                    self.assertIsNone(row["checked_in_at"])
                    self.assertIsNone(row["checked_out_at"])
                    self.assertEqual(clock.call_count, 1, "One instant per response")
                with patch.object(api, "now", return_value=current) as clock:
                    response = self.post("/identify", {"captain_student_id": "1"})
                row = response.json()["data"]["bookings"][0]
                self.assertEqual((row["status"], row["usage_status"]), (expected, "reserved"))
                self.assertEqual(clock.call_count, 1)
        # Merely crossing the schedule boundaries must not mutate usage history.
        with self.Session() as db:
            row = db.get(PrinterBooking, booking["id"])
            self.assertEqual(row.status, "reserved")
            self.assertIsNone(row.checked_in_at)
            self.assertIsNone(row.checked_out_at)
            self.assertIsNone(row.previous_booking_id)
            self.assertIsNone(row.previous_team_name)

    def test_usage_status_precedence_and_timezone_serialization(self):
        booking = self.reserve().json()["data"]
        start, end = self.future, self.future + timedelta(hours=1)
        for raw_status in ("cancelled", "completed", "in_use"):
            with self.Session() as db:
                row = db.get(PrinterBooking, booking["id"])
                row.status = raw_status
                row.checked_in_at = start - timedelta(minutes=5) if raw_status != "cancelled" else None
                row.checked_out_at = start if raw_status == "completed" else None
                db.commit()
            for current in (start - timedelta(hours=1), start, end, end + timedelta(days=1)):
                with self.subTest(raw=raw_status, current=current):
                    with patch.object(api, "now", return_value=current):
                        row = self.client.get("/api/v1/printers/my-bookings", headers=self.headers).json()["data"][0]
                    self.assertEqual(row["status"], raw_status)
                    self.assertEqual(row["usage_status"], raw_status)
                    if raw_status == "completed":
                        self.assertIsNotNone(row["checked_out_at"])
                    elif raw_status == "in_use":
                        self.assertIsNone(row["checked_out_at"])
        # Equivalent aware UTC instants and naive Beijing database values agree.
        from datetime import timezone
        utc_start = start.replace(tzinfo=api.TZ).astimezone(timezone.utc)
        item = SimpleNamespace(id=999, printer_id=1, team_name="timezone",
                               start_time=utc_start, end_time=end.replace(tzinfo=api.TZ),
                               status="reserved", checked_in_at=None, checked_out_at=None)
        with patch.object(api, "now", return_value=utc_start):
            data = api.booking_data(item)
        self.assertEqual((data["status"], data["usage_status"]), ("in_use", "reserved"))
        self.assertEqual(data["start_time"], start.replace(tzinfo=api.TZ).isoformat())

    def test_schedule_projection_does_not_replace_actual_checkin_and_handover(self):
        previous, current = self.seed_use()
        with self.Session() as db:
            start = db.get(PrinterBooking, current).start_time
            end = db.get(PrinterBooking, current).end_time
        with patch.object(api, "now", return_value=start):
            visible = self.client.get("/api/v1/printers/my-bookings", headers=self.headers).json()["data"][0]
            self.assertEqual((visible["status"], visible["usage_status"]), ("in_use", "reserved"))
            self.assertIsNone(visible["checked_in_at"])
            response = self.post(f"/bookings/{current}/check-in")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["data"]["usage_status"], "in_use")
        self.assertEqual(response.json()["data"]["previous_booking_id"], previous)
        self.assertEqual(response.json()["data"]["checked_in_at"], api.iso(start))
        # Time expiry cannot fabricate a return or end actual ongoing usage.
        with patch.object(api, "now", return_value=end + timedelta(hours=1)):
            row = self.client.get("/api/v1/printers/my-bookings", headers=self.headers).json()["data"][0]
            self.assertEqual((row["status"], row["usage_status"]), ("in_use", "in_use"))
            self.assertIsNone(row["checked_out_at"])
            self.assertEqual(self.post(f"/bookings/{current}/check-in").status_code, 409)
            report = self.post(f"/bookings/{current}/incidents", {"description": "超时使用时报告异常"})
            self.assertEqual(report.status_code, 200)
            self.assertEqual(report.json()["data"]["previous_booking_id"], previous)
            response = self.post(f"/bookings/{current}/check-out")
        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.json()["data"]["status"], response.json()["data"]["usage_status"]), ("completed", "completed"))
        self.assertEqual(response.json()["data"]["checked_out_at"], api.iso(end + timedelta(hours=1)))

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

    def test_existing_captain_identify_scope_and_event(self):
        r = self.post("/identify", {"captain_student_id": "1"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["data"]["team"]["id"], 1)
        self.assertEqual(self.post("/identify", {"captain_student_id": "member1"}).status_code, 404)
        self.assertEqual(self.post("/identify", {"captain_student_id": "3"}).status_code, 404)
        self.assertEqual(self.post("/teams", {}).status_code, 404)
        self.assertEqual(self.client.get("/api/v1/printers/my-bookings").status_code, 401)
        old_token = api.create_access_token({"sub": "0", "scope": "printer_team", "printer_team_id": 1})
        self.assertEqual(self.client.get("/api/v1/printers/my-bookings", headers={"Authorization": "Bearer " + old_token}).status_code, 401)
        self.assertEqual(self.client.get("/api/v1/printers/admin/config", headers=self.headers).status_code, 401)
        with self.Session() as db:
            db.get(Team, 1).delete_requested = True
            db.commit()
        self.assertEqual(self.reserve().status_code, 404)

    def test_same_team_three_machines_and_admin_add_delete(self):
        for i in (1, 2, 3):
            self.assertEqual(self.reserve(printer_id=i).status_code, 200)
        self.assertIn(self.client.get("/api/v1/printers/admin/bookings").status_code, (401, 403))
        self.admin()
        payload = {"captain_student_id": "2", "printer_id": 1, "start_time": self.future.isoformat(), "end_time": (self.future + timedelta(hours=1)).isoformat()}
        self.assertEqual(self.post("/admin/bookings", payload).status_code, 409)
        rows = self.client.get("/api/v1/printers/admin/bookings").json()["data"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(self.client.delete(f"/api/v1/printers/admin/bookings/{rows[0]['id']}").status_code, 200)
        payload["printer_id"] = rows[0]["printer_id"]
        self.assertEqual(self.post("/admin/bookings", payload).status_code, 200)
        with self.Session() as db:
            self.assertEqual(db.get(PrinterBooking, rows[0]["id"]).deleted_by, 99)

    def test_auto_event_selection_safe_and_admin_binding(self):
        with self.Session() as db:
            db.get(CompetitionEvent, 1).name = "其他赛事"
            db.commit()
        cfg = self.client.get("/api/v1/printers/config").json()["data"]
        self.assertIsNone(cfg["event"])
        self.assertEqual(self.post("/identify", {"captain_student_id": "1"}).status_code, 409)
        self.admin()
        response = self.client.put("/api/v1/printers/admin/config", json={"event_id": 1})
        self.assertEqual(response.json()["data"]["event"]["id"], 1)
        self.assertEqual(self.post("/identify", {"captain_student_id": "1"}).status_code, 200)

    def test_cancel_authorization_and_reuse(self):
        b = self.reserve().json()["data"]
        other = {"Authorization": "Bearer " + api.create_access_token({"sub": "0", "scope": "printer_team", "competition_team_id": 2, "module_key": "bambu_cup", "captain_student_id": "2"})}
        self.assertEqual(self.post(f'/bookings/{b["id"]}/cancel', headers=other).status_code, 403)
        self.assertEqual(self.post(f'/bookings/{b["id"]}/cancel').status_code, 200)
        self.assertEqual(self.reserve().status_code, 200)
        self.assertEqual(self.post(f'/bookings/{b["id"]}/check-in').status_code, 409)

    def test_my_bookings_cancelled_last_after_cancel_and_identify(self):
        early = self.reserve().json()["data"]
        later = self.reserve(self.future + timedelta(hours=2)).json()["data"]
        latest = self.reserve(self.future + timedelta(hours=4)).json()["data"]
        self.assertEqual(self.post(f'/bookings/{latest["id"]}/cancel').status_code, 200)
        expected = [later["id"], early["id"], latest["id"]]
        rows = self.client.get("/api/v1/printers/my-bookings", headers=self.headers).json()["data"]
        self.assertEqual([b["id"] for b in rows], expected)
        identity = self.post("/identify", {"captain_student_id": "1"}).json()["data"]
        self.assertEqual([b["id"] for b in identity["bookings"]], expected)
        self.assertEqual(self.post(f'/bookings/{later["id"]}/cancel').status_code, 200)
        rows = self.client.get("/api/v1/printers/my-bookings", headers=self.headers).json()["data"]
        self.assertEqual([b["id"] for b in rows], [early["id"], latest["id"], later["id"]])

    def seed_use(self):
        t = api.now().replace(microsecond=0)
        with self.Session() as db:
            prev = PrinterBooking(printer_id=1, competition_team_id=2, team_name="Previous actual team", captain_name="Previous captain", captain_student_id="2", start_time=t-timedelta(hours=4), end_time=t-timedelta(hours=3), status="completed", checked_in_at=t-timedelta(hours=4), checked_out_at=t-timedelta(hours=3))
            unused = PrinterBooking(printer_id=1, competition_team_id=2, team_name="Never checked in", captain_name="Unused", captain_student_id="2", start_time=t-timedelta(hours=2), end_time=t-timedelta(hours=1), status="reserved")
            current = PrinterBooking(printer_id=1, competition_team_id=1, team_name="Team 1", captain_name="Captain 1", captain_student_id="1", start_time=t-timedelta(minutes=1), end_time=t+timedelta(minutes=30), status="reserved")
            future = PrinterBooking(printer_id=1, competition_team_id=2, team_name="Future team", captain_name="Future", captain_student_id="2", start_time=t+timedelta(hours=1), end_time=t+timedelta(hours=2), status="reserved")
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

    def test_early_checkout_releases_remaining_slot_for_other_team(self):
        _, current = self.seed_use()
        moment = api.now().replace(microsecond=0)
        start = moment + timedelta(minutes=1)
        end = moment + timedelta(minutes=20)
        other = {"Authorization": "Bearer " + api.create_access_token({"sub": "0", "scope": "printer_team", "competition_team_id": 2, "module_key": "bambu_cup", "captain_student_id": "2"})}
        payload = {"printer_id": 1, "start_time": start.isoformat(), "end_time": end.isoformat()}
        with patch.object(api, "now", return_value=moment):
            self.assertEqual(self.post(f"/bookings/{current}/check-in").status_code, 200)
            self.assertEqual(self.post("/bookings", payload, other).status_code, 409)
            result = self.post(f"/bookings/{current}/check-out")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json()["data"]["occupied_until"], api.iso(moment))
            self.assertEqual(self.post("/bookings", payload, other).status_code, 200)
            self.assertEqual(self.post("/bookings", payload).status_code, 409)
            self.admin()
            admin_payload = {**payload, "captain_student_id": "2", "start_time": end.isoformat(), "end_time": (end + timedelta(minutes=5)).isoformat()}
            self.assertEqual(self.post("/admin/bookings", admin_payload).status_code, 200)
        with self.Session() as db:
            original = db.get(PrinterBooking, current)
            self.assertEqual(original.status, "completed")
            self.assertEqual(original.checked_out_at, moment)
            self.assertGreater(original.end_time, end)
            self.assertIsNotNone(original.checked_in_at)

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

    def test_legacy_migration_preserves_unmatched_and_incidents(self):
        from scripts.init_printers import migrate_printers
        # Construct the previous release's schema with a distinct legacy id=1.
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE printer_incidents"))
            conn.execute(text("DROP TABLE printer_bookings"))
            conn.execute(text("CREATE TABLE printer_teams (id INTEGER PRIMARY KEY, module_key VARCHAR(80), captain_student_id VARCHAR(30))"))
            conn.execute(text("INSERT INTO printer_teams VALUES (1, 'bambu_cup', '2'), (2, 'bambu_cup', 'not-found')"))
            booking_ddl = "CREATE TABLE printer_bookings (id INTEGER PRIMARY KEY, printer_id INTEGER NOT NULL, team_id INTEGER NOT NULL, team_name VARCHAR(100) NOT NULL, captain_name VARCHAR(50) NOT NULL, captain_student_id VARCHAR(30) NOT NULL, start_time DATETIME NOT NULL, end_time DATETIME NOT NULL, purpose VARCHAR(500), status VARCHAR(20), checked_in_at DATETIME, checked_out_at DATETIME, previous_booking_id INTEGER, previous_team_name VARCHAR(100), created_at DATETIME, updated_at DATETIME, FOREIGN KEY (team_id) REFERENCES printer_teams(id), FOREIGN KEY (previous_booking_id) REFERENCES printer_bookings(id))"
            if self.engine.dialect.name == "mysql":
                booking_ddl = booking_ddl.replace("id INTEGER PRIMARY KEY", "id INTEGER PRIMARY KEY AUTO_INCREMENT", 1)
            conn.execute(text(booking_ddl))
            conn.execute(text("INSERT INTO printer_bookings(id,printer_id,team_id,team_name,captain_name,captain_student_id,start_time,end_time,purpose,status,created_at,updated_at) VALUES (1,1,1,'legacy matched','captain','2','2026-01-01 09:00:00','2026-01-01 10:00:00','','completed','2026-01-01 09:00:00','2026-01-01 10:00:00'),(2,2,2,'legacy unmatched','captain','not-found','2026-01-01 09:00:00','2026-01-01 10:00:00','','completed','2026-01-01 09:00:00','2026-01-01 10:00:00')"))
        # Preserve actual incident and self-reference foreign keys during migration.
        PrinterIncident.__table__.create(self.engine)
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE printer_bookings SET previous_booking_id=1 WHERE id=2"))
            conn.execute(text("INSERT INTO printer_incidents(id,printer_id,booking_id,reporter_team_name,previous_booking_id,responsible_team_name,description,created_at,updated_at) VALUES (1,2,2,'legacy unmatched',1,'legacy matched','historical incident','2026-01-01 09:00:00','2026-01-01 10:00:00')"))
        migrate_printers(self.engine)
        migrate_printers(self.engine)
        with self.Session() as db:
            self.assertEqual(db.get(PrinterBooking, 1).competition_team_id, 2)
            self.assertIsNone(db.get(PrinterBooking, 2).competition_team_id)
            self.assertEqual(db.get(PrinterBooking, 2).team_name, "legacy unmatched")
            self.assertEqual(db.get(PrinterBooking, 2).previous_booking_id, 1)
            self.assertEqual(db.get(PrinterIncident, 1).responsible_team_name, "legacy matched")
        self.assertEqual(self.reserve().status_code, 200)
        with self.engine.begin() as conn:
            if self.engine.dialect.name == "mysql":
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            conn.execute(text("DROP TABLE printer_teams"))
            if self.engine.dialect.name == "mysql":
                conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

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
