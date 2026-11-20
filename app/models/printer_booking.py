"""Printer reservations reference the existing competition teams.

Legacy printer_teams tables remain untouched but are no longer mapped or written.
Datetimes are stored as naive Asia/Shanghai values.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from app.models.base import BaseModel


def beijing_now():
    return datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None)


class PrinterBase(BaseModel):
    __abstract__ = True
    created_at = Column(DateTime, default=beijing_now, nullable=False)
    updated_at = Column(DateTime, default=beijing_now, onupdate=beijing_now, nullable=False)


class Printer(PrinterBase):
    __tablename__ = "printers"
    __table_args__ = {"mysql_engine": "InnoDB"}
    name = Column(String(80), nullable=False)
    status = Column(String(20), nullable=False, default="available")


class PrinterConfig(PrinterBase):
    __tablename__ = "printer_configs"
    __table_args__ = {"mysql_engine": "InnoDB"}
    module_key = Column(String(80), nullable=False, default="")
    opening_hours_enabled = Column(Boolean, nullable=False, default=False)
    opening_hours = Column(JSON, nullable=False, default=list)
    admin_contact = Column(String(300), nullable=True)


class PrinterBooking(PrinterBase):
    __tablename__ = "printer_bookings"
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    # Retained only to preserve old database rows; never used for new identity.
    team_id = Column(Integer, nullable=True)
    competition_team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    team_name = Column(String(100), nullable=False)
    captain_name = Column(String(50), nullable=False)
    captain_student_id = Column(String(30), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    purpose = Column(String(500), nullable=False, default="")
    status = Column(String(20), nullable=False, default="reserved")
    # 兼容旧签到历史，自动开始流程不依赖或伪造该字段。
    checked_in_at = Column(DateTime, nullable=True)
    checked_out_at = Column(DateTime, nullable=True)
    previous_booking_id = Column(Integer, ForeignKey("printer_bookings.id"), nullable=True)
    previous_team_name = Column(String(100), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    __table_args__ = (Index("ix_printer_booking_overlap", "printer_id", "status", "start_time", "end_time"), {"mysql_engine": "InnoDB"})


class PrinterIncident(PrinterBase):
    __tablename__ = "printer_incidents"
    __table_args__ = {"mysql_engine": "InnoDB"}
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("printer_bookings.id"), nullable=False)
    reporter_team_name = Column(String(100), nullable=False)
    previous_booking_id = Column(Integer, ForeignKey("printer_bookings.id"), nullable=True)
    responsible_team_name = Column(String(100), nullable=True)
    responsible_captain_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, nullable=True)


PRINTER_TABLES = [Printer.__table__, PrinterConfig.__table__, PrinterBooking.__table__, PrinterIncident.__table__]


START_WINDOWS = (("09:00", "12:00"), ("14:00", "17:00"), ("19:00", "21:30"))
# 五山下架单色 A1，保留多色 A1；设备 ID 不重排，避免历史关联错位。
RETIRED_PRINTER_NAMES = {1: "五山 A1 单色"}
PRINTER_NAMES = {
    2: "五山 A1 多色",
    3: "五山 X2D",
    4: "大学城 A1",
    5: "大学城 A2 单机",
    6: "大学城 A2L 多色",
}


def daily_opening_hours():
    return [
        {"weekday": day, "start": start, "end": end}
        for day in range(7) for start, end in START_WINDOWS
    ]


def initialize_printers(db):
    """Update the fleet in place so existing booking and incident IDs stay linked."""
    cfg = db.get(PrinterConfig, 1)
    if cfg is None:
        cfg = PrinterConfig(id=1, module_key="")
        db.add(cfg)
    cfg.opening_hours_enabled = True
    cfg.opening_hours = daily_opening_hours()
    # 旧库只停用已有设备，新库不再创建；保留所有历史预约和异常记录。
    for printer_id in RETIRED_PRINTER_NAMES:
        printer = db.get(Printer, printer_id)
        if printer is not None:
            printer.status = "maintenance"
    for printer_id, name in PRINTER_NAMES.items():
        printer = db.get(Printer, printer_id)
        if printer is None:
            db.add(Printer(id=printer_id, name=name, status="available"))
        else:
            printer.name = name
    db.commit()
