"""Printer reservations use independent tables; stored datetimes are naive Asia/Shanghai."""
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index, UniqueConstraint
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
    module_key = Column(String(80), nullable=False, default="bambu_cup")
    opening_hours_enabled = Column(Boolean, nullable=False, default=False)
    opening_hours = Column(JSON, nullable=False, default=list)
    registration_code_hash = Column(String(255), nullable=True)
    registration_enabled = Column(Boolean, nullable=False, default=False)


class PrinterTeam(PrinterBase):
    __tablename__ = "printer_teams"
    module_key = Column(String(80), nullable=False)
    team_name = Column(String(100), nullable=False)
    captain_name = Column(String(50), nullable=False)
    captain_student_id = Column(String(30), nullable=False)
    captain_phone_hash = Column(String(255), nullable=False)
    access_code_hash = Column(String(255), nullable=False)
    __table_args__ = (UniqueConstraint("module_key", "captain_student_id", name="uq_printer_team_captain"), {"mysql_engine": "InnoDB"})


class PrinterBooking(PrinterBase):
    __tablename__ = "printer_bookings"
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("printer_teams.id"), nullable=False)
    team_name = Column(String(100), nullable=False)
    captain_name = Column(String(50), nullable=False)
    captain_student_id = Column(String(30), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    purpose = Column(String(500), nullable=False, default="")
    status = Column(String(20), nullable=False, default="reserved")
    checked_in_at = Column(DateTime, nullable=True)
    checked_out_at = Column(DateTime, nullable=True)
    previous_booking_id = Column(Integer, ForeignKey("printer_bookings.id"), nullable=True)
    previous_team_name = Column(String(100), nullable=True)
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


PRINTER_TABLES = [Printer.__table__, PrinterConfig.__table__, PrinterTeam.__table__, PrinterBooking.__table__, PrinterIncident.__table__]


def initialize_printers(db):
    """Run once before serving requests, safe to repeat; never overwrites configuration."""
    if not db.get(PrinterConfig, 1):
        db.add(PrinterConfig(id=1, module_key="bambu_cup", opening_hours_enabled=False,
                             opening_hours=[{"weekday": i, "start": "09:00", "end": "18:00"} for i in range(7)]))
    for i in range(1, 4):
        if not db.get(Printer, i):
            db.add(Printer(id=i, name=f"拓竹 {i} 号机", status="available"))
    db.commit()
