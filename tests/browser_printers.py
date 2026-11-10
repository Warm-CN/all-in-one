"""Browser acceptance against running local frontend/backend, isolated DB only.

Run with system Python (Playwright installed):
  python tests/browser_printers.py --url http://127.0.0.1:3000
Seed credentials through PRINTER_E2E_* environment variables. Never use production.
"""
import argparse
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:3000')
    args = parser.parse_args()
    out = Path('frontend/coverage/printers')
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        errors = []
        page = browser.new_page(viewport={'width': 1440, 'height': 1080}, timezone_id='Asia/Shanghai')
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url + '/printer-booking', wait_until='networkidle')
        page.get_by_role('heading', name='打印机预约中心').wait_for()
        assert page.locator('.machine-card').count() == 3, 'Expected three printers'
        assert page.locator('.el-alert--error').count() == 0, 'Initial API load failed'
        page.screenshot(path=str(out / 'desktop.png'), full_page=True)
        for tab in ['预约时间', '我的预约', '队伍身份', '设备日程']:
            page.get_by_role('button', name=tab, exact=True).click()
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile horizontal overflow'
        page.screenshot(path=str(out / 'mobile.png'), full_page=True)
        page.get_by_role('button', name='队伍身份', exact=True).click()
        if os.getenv('PRINTER_E2E_SID'):
            fields = page.locator('.form-grid input')
            fields.nth(0).fill(os.environ['PRINTER_E2E_SID'])
            fields.nth(1).fill(os.environ['PRINTER_E2E_PHONE'])
            fields.nth(2).fill(os.environ['PRINTER_E2E_PASSWORD'])
            page.get_by_role('button', name='核验队伍', exact=True).click()
            page.get_by_text('队伍核验成功', exact=True).wait_for()
            page.get_by_role('heading', name='我的预约', exact=True).wait_for()
            page.screenshot(path=str(out / 'my-bookings-mobile.png'), full_page=True)
            page.get_by_role('button', name='设备日程', exact=True).click()
            page.get_by_role('button', name='预约这台设备', exact=True).first.click()
            page.get_by_placeholder('如：底盘支架、外壳原型').fill('浏览器验收模型')
            page.get_by_role('button', name='确认预约', exact=True).click()
            page.get_by_text('预约成功', exact=True).wait_for()
            card = page.locator('.booking-card').filter(has_text='浏览器验收模型').filter(has=page.get_by_role('button', name='取消预约', exact=True)).first
            card.get_by_role('button', name='取消预约', exact=True).click()
            page.get_by_role('button', name='确认', exact=True).click()
            page.get_by_text('操作成功', exact=True).wait_for()
        if os.getenv('PRINTER_E2E_ADMIN'):
            response = page.request.post(args.url + '/api/v1/auth/login', data={'student_id': os.environ['PRINTER_E2E_ADMIN'], 'password': os.environ['PRINTER_E2E_ADMIN_PASSWORD']})
            assert response.ok, response.status
            data = response.json()['data']
            page.evaluate('(data) => { localStorage.setItem("token", data.token.access_token); localStorage.setItem("userInfo", JSON.stringify(data.user)) }', data)
            page.goto(args.url + '/admin/printers', wait_until='networkidle')
            page.get_by_role('heading', name='打印机管理', exact=True).wait_for()
            assert page.locator('.devices article').count() == 3
            assert page.locator('.el-alert--error').count() == 0
            page.screenshot(path=str(out / 'admin-mobile.png'), full_page=True)
            page.set_viewport_size({'width': 1440, 'height': 1080})
            page.screenshot(path=str(out / 'admin-desktop.png'), full_page=True)
        assert not errors, errors
        checks = ['three_printers', 'public_tabs', 'mobile_no_overflow', 'no_js_errors']
        if os.getenv('PRINTER_E2E_SID'):
            checks += ['team_identity', 'create_booking', 'cancel_booking']
        if os.getenv('PRINTER_E2E_ADMIN'):
            checks += ['admin_identity', 'admin_page_three_printers']
        print(json.dumps({'status': 'passed', 'checks': checks, 'screenshots': str(out)}, ensure_ascii=False))
        browser.close()


if __name__ == '__main__':
    main()
