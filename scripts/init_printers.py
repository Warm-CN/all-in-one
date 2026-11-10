"""Incremental printer migration, run BEFORE restarting backend.

python -m scripts.init_printers
Only creates printer tables; competition_events/teams must already exist.
Legacy printer_teams and unmatched bookings are preserved without reassignment.
"""
import argparse
import re
import sys
from pathlib import Path
from sqlalchemy import inspect, text, MetaData, Table, select
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.database import Base, engine, SessionLocal
from app.models.printer_booking import PRINTER_TABLES, PrinterBooking, PrinterConfig, initialize_printers


def migrate_printers(target_engine):
    """Idempotent schema extension and conservative old-team linking."""
    existing = inspect(target_engine).get_table_names()
    if "teams" not in existing or "competition_events" not in existing:
        raise RuntimeError("请先初始化原系统的 teams/competition_events 表；打印机模块不会另建队伍数据库")
    if "printer_bookings" in existing:
        with target_engine.connect() as conn:
            dialect = target_engine.dialect.name
            columns = {c["name"]: c for c in inspect(conn).get_columns("printer_bookings")}
            if "competition_team_id" not in columns:
                if dialect == "mysql":
                    conn.execute(text("ALTER TABLE printer_bookings ADD COLUMN competition_team_id INTEGER NULL, ADD CONSTRAINT fk_printer_existing_team FOREIGN KEY (competition_team_id) REFERENCES teams(id) ON DELETE SET NULL"))
                else:
                    conn.execute(text("ALTER TABLE printer_bookings ADD COLUMN competition_team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL"))
            if "deleted_by" not in columns:
                conn.execute(text("ALTER TABLE printer_bookings ADD COLUMN deleted_by INTEGER NULL"))
            if "team_id" in columns and not columns["team_id"]["nullable"]:
                if dialect == "mysql":
                    conn.execute(text("ALTER TABLE printer_bookings MODIFY COLUMN team_id INTEGER NULL"))
                elif dialect == "sqlite":
                    conn.commit()
                    conn.execute(text("PRAGMA foreign_keys=OFF"))
                    sql = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='printer_bookings'")).scalar_one()
                    sql = re.sub(r"(?i)CREATE TABLE\s+[\"`\[]?printer_bookings[\"`\]]?", "CREATE TABLE printer_bookings_migrating", sql, count=1)
                    sql = re.sub(r"(?im)(\bteam_id\s+INTEGER)\s+NOT NULL", r"\1", sql)
                    cols = [c["name"] for c in inspect(conn).get_columns("printer_bookings")]
                    quoted = ",".join('"' + c + '"' for c in cols)
                    conn.execute(text(sql))
                    conn.execute(text(f"INSERT INTO printer_bookings_migrating ({quoted}) SELECT {quoted} FROM printer_bookings"))
                    conn.execute(text("DROP TABLE printer_bookings"))
                    conn.execute(text("ALTER TABLE printer_bookings_migrating RENAME TO printer_bookings"))
                    conn.commit()
                    conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()
    Base.metadata.create_all(target_engine, tables=PRINTER_TABLES)
    # Recreate missing indexes after SQLite's safe table rebuild.
    for index in PrinterBooking.__table__.indexes:
        index.create(target_engine, checkfirst=True)
    with target_engine.begin() as conn:
        if "printer_teams" in existing:
            legacy = Table("printer_teams", MetaData(), autoload_with=conn)
            bookings = PrinterBooking.__table__
            from app.models.team import Team
            for old in conn.execute(select(legacy.c.id, legacy.c.module_key, legacy.c.captain_student_id)).mappings():
                matches = conn.execute(select(Team.id).where(Team.module_key == old["module_key"], Team.captain_student_id == old["captain_student_id"])).scalars().all()
                if len(matches) == 1:
                    conn.execute(bookings.update().where(bookings.c.team_id == old["id"], bookings.c.competition_team_id.is_(None)).values(competition_team_id=matches[0]))
        # Existing legacy config columns may have NOT NULL without server defaults.
        reflected = Table("printer_configs", MetaData(), autoload_with=conn)
        if not conn.execute(select(reflected.c.id).where(reflected.c.id == 1)).first():
            from app.models.printer_booking import beijing_now
            values = dict(id=1, module_key="", opening_hours_enabled=False, opening_hours=[], created_at=beijing_now(), updated_at=beijing_now())
            if "registration_enabled" in reflected.c:
                values["registration_enabled"] = False
            conn.execute(reflected.insert().values(**values))
    from sqlalchemy.orm import Session
    with Session(target_engine) as db:
        initialize_printers(db)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    migrate_printers(engine)
    print("打印机迁移完成：复用现有赛事及队伍，旧记录保留，三台设备就绪。")


if __name__ == "__main__":
    main()
