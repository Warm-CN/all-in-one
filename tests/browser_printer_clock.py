"""Verify open production pages cross reservation boundaries without reload.
Run against local Vite preview: python tests/browser_printer_clock.py
"""
import json
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:4173'


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.clock.install(time=__import__('datetime').datetime.fromisoformat('2026-11-10T14:59:59+08:00'))
        booking = {'id': 1, 'printer_id': 1, 'team_name': '时间边界测试队', 'captain_phone': '13800000000', 'status': 'reserved', 'usage_status': 'reserved', 'start_time': '2026-11-10T15:00:10+08:00', 'end_time': '2026-11-10T16:00:00+08:00', 'checked_in_at': None, 'checked_out_at': None}
        cfg = {'printers': [{'id': i, 'name': f'拓竹 {i} 号机', 'status': 'available'} for i in range(1, 4)], 'opening_hours': [], 'admin_contact': '测试管理员：13900000000', 'event': {'id': 1, 'name': '拓竹杯'}, 'signup_url': '/team-portal?event_id=1'}
        def respond(route):
            path = route.request.url.split('/api/v1/printers')[-1].split('?')[0]
            data = cfg if path.endswith('/config') else ([booking] if path.endswith('/bookings') or path == '/my-bookings' else [])
            route.fulfill(json={'code': 200, 'data': data})
        page.route('**/api/**', lambda route: route.fulfill(json={'code': 200, 'data': {'role': 'admin', 'real_name': '测试'}}) if '/auth/me' in route.request.url else route.fulfill(json={'code': 200, 'data': []}))
        page.route('**/api/v1/printers/**', respond)
        page.goto(BASE + '/printer-booking', wait_until='networkidle')
        assert page.locator('.captain-contact a').get_attribute('href') == 'tel:13800000000'
        assert page.locator('.admin-contact-panel').get_by_text('测试管理员：13900000000', exact=True).count() == 1
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        slot = page.locator('.slot-list')
        assert slot.get_by_text('待使用', exact=True).count() == 1
        page.clock.fast_forward(12000)
        assert slot.get_by_text('待确认开始', exact=True).count() == 1
        page.clock.fast_forward(300000)
        assert slot.locator('li').count() == 0
        booking.update(status='in_use', usage_status='in_use', checked_in_at='2026-11-10T15:00:10+08:00')
        page.evaluate("localStorage.setItem('token','clock-test'); localStorage.setItem('userInfo', JSON.stringify({role:'admin',real_name:'测试'}))")
        page.clock.set_system_time(__import__('datetime').datetime.fromisoformat('2026-11-10T14:59:59+08:00'))
        page.goto(BASE + '/admin/printers', wait_until='networkidle')
        row = page.locator('.admin-bookings')
        row.get_by_text('使用中', exact=True).wait_for(timeout=5000)
        page.clock.fast_forward(12000)
        assert row.get_by_text('使用中', exact=True).count() == 1
        page.clock.fast_forward(3600000)
        assert row.get_by_text('已结束', exact=True).count() == 1
        booking.update(status='completed', usage_status='completed', checked_out_at='2026-11-10T15:20:00+08:00', occupied_until='2026-11-10T15:20:00+08:00')
        page.goto(BASE + '/printer-booking', wait_until='networkidle')
        assert page.locator('.slot-list').get_by_text('15:00 – 15:20', exact=True).count() == 1
        assert page.locator('.slot-list').get_by_text('已归还', exact=True).count() == 1
        assert not errors, errors
        print(json.dumps({'status': 'passed', 'checks': ['public_live_start_end', 'admin_live_start_end', 'no_reload', 'no_fake_checkin', 'captain_phone_tel_link', 'admin_contact_display', 'mobile_no_overflow']}, ensure_ascii=False))
        browser.close()


if __name__ == '__main__':
    main()
