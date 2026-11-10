import test from 'node:test'
import assert from 'node:assert/strict'
import { scheduleTime } from '../frontend/src/utils/printerTime.js'

test('cross-day labels include the exact Beijing time', () => {
  assert.equal(scheduleTime('2026-11-09T23:15:00+08:00', '2026-11-10'), '昨日 23:15')
  assert.equal(scheduleTime('2026-11-11T06:30:00+08:00', '2026-11-10'), '次日 06:30')
  assert.equal(scheduleTime('2026-11-10T22:00:00', '2026-11-10'), '22:00')
})
test('multi-day and year boundaries remain unambiguous', () => {
  assert.equal(scheduleTime('2026-11-08T20:10:00+08:00', '2026-11-10'), '2026-11-08 20:10')
  assert.equal(scheduleTime('2026-11-12T07:00:00+08:00', '2026-11-10'), '2026-11-12 07:00')
  assert.equal(scheduleTime('2027-01-01T01:20:00+08:00', '2026-12-31'), '次日 01:20')
  assert.equal(scheduleTime('2026-12-31T22:30:00Z', '2026-12-31'), '次日 06:30')
})
