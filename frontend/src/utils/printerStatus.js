// Time limits also apply while a page is open, before the next server refresh.
export function usageStatus(booking) {
  return booking.usage_status ?? booking.status;
}

const instant = (value) =>
  new Date(
    /(Z|[+-]\d\d:\d\d)$/.test(value) ? value : `${value}+08:00`,
  ).getTime();

export function checkInDeadline(booking) {
  return booking.check_in_deadline
    ? instant(booking.check_in_deadline)
    : Math.min(
        instant(booking.start_time) + 5 * 60000,
        instant(booking.end_time),
      );
}

export function reservationStatus(booking, now = Date.now()) {
  const usage = usageStatus(booking);
  if (usage === "cancelled" || usage === "completed") return usage;
  if (usage === "reserved") {
    if (now >= checkInDeadline(booking)) return "cancelled";
    return now < instant(booking.start_time) ? "reserved" : "in_use";
  }
  return now >= instant(booking.end_time) ? "completed" : usage;
}

export function reservationLabel(booking, now = Date.now()) {
  const status = reservationStatus(booking, now);
  if (status === "completed")
    return booking.checked_out_at ? "已归还" : "已结束";
  if (status === "in_use" && usageStatus(booking) === "reserved")
    return "待确认开始";
  return (
    { reserved: "待使用", in_use: "使用中", cancelled: "已取消" }[status] ||
    status
  );
}
