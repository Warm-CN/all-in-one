import test from 'node:test'
import assert from 'node:assert/strict'
import { reservationStatus, reservationLabel } from '../frontend/src/utils/printerStatus.js'

const start = Date.parse('2026-11-10T15:00:00+08:00')
const end = Date.parse('2026-11-10T16:00:00+08:00')
const booking = {
  usage_status: 'reserved',
  start_time: '2026-11-10T15:00:00+08:00',
  end_time: '2026-11-10T16:00:00+08:00',
}

test('an open page derives start and end from the scheduled times', () => {
  assert.equal(reservationStatus(booking, start - 1), 'reserved')
  assert.equal(reservationLabel(booking, start), '使用中')
  assert.equal(reservationStatus(booking, start + 30 * 60000), 'in_use')
  assert.equal(reservationStatus(booking, end - 1), 'in_use')
  assert.equal(reservationLabel(booking, end), '已结束')
  assert.equal(reservationLabel({ ...booking, usage_status: 'in_use' }, end), '已结束')
})

test('a short reservation also ends automatically', () => {
  const short = { ...booking, end_time: '2026-11-10T15:02:00+08:00' }
  assert.equal(reservationStatus(short, start + 120000 - 1), 'in_use')
  assert.equal(reservationStatus(short, start + 120000), 'completed')
})

test('cancellation and early return take precedence over the clock', () => {
  assert.equal(reservationStatus({ ...booking, usage_status: 'cancelled' }, start), 'cancelled')
  const returned = { ...booking, usage_status: 'completed', checked_out_at: '2026-11-10T15:01:00+08:00' }
  assert.equal(reservationLabel(returned, start + 60000), '已归还')
})
