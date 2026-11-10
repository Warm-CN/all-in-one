// Reservation progress follows the clock; actual handover remains an explicit action.
export function usageStatus(booking) {
  return booking.usage_status ?? booking.status;
}

export function reservationStatus(booking, now = Date.now()) {
  const usage = usageStatus(booking);
  if (usage !== "reserved") return usage;
  const instant = (value) =>
    new Date(
      /(Z|[+-]\d\d:\d\d)$/.test(value) ? value : `${value}+08:00`,
    ).getTime();
  if (now < instant(booking.start_time)) return "reserved";
  return now < instant(booking.end_time) ? "in_use" : "completed";
}

export function reservationLabel(booking, now = Date.now()) {
  const status = reservationStatus(booking, now);
  if (status === "completed")
    return booking.checked_out_at ? "已归还" : "已结束";
  return (
    { reserved: "待使用", in_use: "使用中", cancelled: "已取消" }[status] ||
    status
  );
}
