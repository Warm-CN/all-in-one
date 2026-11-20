// Time limits also apply while a page is open, before the next server refresh.
export function usageStatus(booking) {
  return booking.usage_status ?? booking.status;
}

const instant = (value) =>
  new Date(
    /(Z|[+-]\d\d:\d\d)$/.test(value) ? value : `${value}+08:00`,
  ).getTime();

export function reservationStatus(booking, now = Date.now()) {
  const usage = usageStatus(booking);
  if (usage !== "reserved" && usage !== "in_use") return usage;
  if (now >= instant(booking.end_time)) return "completed";
  return now < instant(booking.start_time) ? "reserved" : "in_use";
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
