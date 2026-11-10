import test from 'node:test'
import assert from 'node:assert/strict'
import { reservationStatus, reservationLabel, usageStatus } from '../frontend/src/utils/printerStatus.js'

const start = Date.parse('2026-11-10T15:00:00+08:00')
const end = Date.parse('2026-11-10T16:00:00+08:00')
const booking = { status: 'reserved', usage_status: 'reserved', start_time: '2026-11-10T15:00:00+08:00', end_time: '2026-11-10T16:00:00+08:00' }

test('reservation changes exactly at start and end without replacing handover state', () => {
  assert.equal(reservationStatus(booking, start - 1), 'reserved')
  assert.equal(reservationStatus(booking, start), 'in_use')
  assert.equal(reservationStatus(booking, end - 1), 'in_use')
  assert.equal(reservationStatus(booking, end), 'completed')
  assert.equal(reservationLabel(booking, end), '已结束')
  assert.equal(usageStatus(booking), 'reserved')
  assert.equal(booking.checked_in_at, undefined)
})

test('server projected state continues to advance in an already open page', () => {
  assert.equal(reservationStatus({ ...booking, status: 'in_use' }, end), 'completed')
  assert.equal(reservationStatus({ ...booking, start_time: '2026-11-10T15:00:00', end_time: '2026-11-10T16:00:00' }, start), 'in_use')
})

test('cancelled, checked out and overdue actual use take precedence over time', () => {
  assert.equal(reservationStatus({ ...booking, usage_status: 'cancelled' }, start), 'cancelled')
  assert.equal(reservationStatus({ ...booking, usage_status: 'in_use' }, end + 1), 'in_use')
  const returned = { ...booking, usage_status: 'completed', checked_out_at: '2026-11-10T15:30:00+08:00' }
  assert.equal(reservationStatus(returned, start), 'completed')
  assert.equal(reservationLabel(returned, end), '已归还')
})
