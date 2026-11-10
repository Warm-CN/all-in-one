import test from 'node:test'
import assert from 'node:assert/strict'
import { reservationStatus, reservationLabel, usageStatus, checkInDeadline } from '../frontend/src/utils/printerStatus.js'
const start = Date.parse('2026-11-10T15:00:00+08:00')
const end = Date.parse('2026-11-10T16:00:00+08:00')
const booking = {status:'reserved', usage_status:'reserved', start_time:'2026-11-10T15:00:00+08:00',end_time:'2026-11-10T16:00:00+08:00'}
test('unconfirmed reservation cancels exactly at five minutes', () => {
  assert.equal(reservationStatus(booking,start-1),'reserved')
  assert.equal(reservationStatus(booking,start),'in_use')
  assert.equal(reservationLabel(booking,start),'待确认开始')
  assert.equal(reservationStatus(booking,start+300000-1),'in_use')
  assert.equal(reservationStatus(booking,start+300000),'cancelled')
  assert.equal(checkInDeadline(booking),start+300000)
  assert.equal(usageStatus(booking),'reserved')
  assert.equal(booking.checked_in_at,undefined)
})
test('confirmed use automatically ends at scheduled end', () => {
  const confirmed={...booking,usage_status:'in_use'}
  assert.equal(reservationStatus(confirmed,end-1),'in_use')
  assert.equal(reservationStatus(confirmed,end),'completed')
  assert.equal(reservationLabel(confirmed,end),'已结束')
})
test('cancel and early return persist, short bookings use earlier deadline', () => {
  assert.equal(reservationStatus({...booking,usage_status:'cancelled'},start),'cancelled')
  const returned={...booking,usage_status:'completed',checked_out_at:'2026-11-10T15:01:00+08:00'}
  assert.equal(reservationLabel(returned,start),'已归还')
  const short={...booking,end_time:'2026-11-10T15:02:00+08:00'}
  assert.equal(checkInDeadline(short),start+120000)
  assert.equal(reservationStatus(short,start+120000),'cancelled')
})
