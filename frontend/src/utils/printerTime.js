// Relative day labels refer to the date selected in the device schedule.
export function scheduleTime(value, selectedDate) {
  if (!value) return '—'
  const input = /(Z|[+-]\d\d:\d\d)$/.test(value) ? value : `${value}+08:00`
  const date = new Date(input)
  if (Number.isNaN(date.getTime())) return '—'
  const beijing = new Date(date.getTime() + 8 * 3600000).toISOString()
  const day = beijing.slice(0, 10)
  const time = beijing.slice(11, 16)
  const difference = (Date.parse(`${day}T00:00:00Z`) - Date.parse(`${selectedDate}T00:00:00Z`)) / 86400000
  if (difference === 0) return time
  if (difference === -1) return `昨日 ${time}`
  if (difference === 1) return `次日 ${time}`
  return `${day} ${time}`
}
