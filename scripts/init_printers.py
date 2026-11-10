"""Idempotently create ONLY printer tables and seed three machines.

python scripts/init_printers.py
python scripts/init_printers.py --set-registration-code  (secure prompt)
Uses the same .env database as the application. Never drops existing tables.
"""
import argparse
import getpass
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.database import Base, engine, SessionLocal
from passlib.hash import pbkdf2_sha256
get_password_hash = pbkdf2_sha256.hash
from app.models.printer_booking import PRINTER_TABLES, PrinterConfig, initialize_printers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-registration-code", action="store_true")
    args = parser.parse_args()
    Base.metadata.create_all(engine, tables=PRINTER_TABLES)
    with SessionLocal() as db:
        initialize_printers(db)
        if args.set_registration_code:
            code = getpass.getpass("打印机报名邀请码（8–72字符，不会显示）: ")
            if not 8 <= len(code) <= 72:
                raise SystemExit("邀请码必须为8–72字符")
            db.get(PrinterConfig, 1).registration_code_hash = get_password_hash(code)
            db.get(PrinterConfig, 1).registration_enabled = True
            db.commit()
    print("打印机专属表已初始化，三台设备就绪；其他表及原有配置保持不变。")


if __name__ == "__main__":
    main()
