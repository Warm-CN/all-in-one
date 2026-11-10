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
        signup_href = page.locator('.signup-link a').get_attribute('href')
        assert 'event_id=' in signup_href, 'Registration must target selected competition'
        if os.getenv('PRINTER_E2E_MEMBER'):
            page.get_by_placeholder('请输入已报名队伍的队长学号').fill(os.environ['PRINTER_E2E_MEMBER'])
            page.get_by_role('button', name='查询队伍', exact=True).click()
            page.get_by_text('未找到该赛事的有效队长队伍，请先报名或联系管理员', exact=False).first.wait_for()
            assert page.get_by_role('button', name='查询队伍', exact=True).is_visible()
        if os.getenv('PRINTER_E2E_SID'):
            assert page.locator('input[type=password]').count() == 0, 'No independent password allowed'
            page.get_by_placeholder('请输入已报名队伍的队长学号').fill(os.environ['PRINTER_E2E_SID'])
            page.get_by_role('button', name='查询队伍', exact=True).click()
            page.get_by_text('已查到参赛队伍', exact=True).wait_for()
            page.get_by_role('heading', name='我的预约', exact=True).wait_for()
            page.screenshot(path=str(out / 'my-bookings-mobile.png'), full_page=True)
            page.get_by_role('button', name='设备日程', exact=True).click()
            page.get_by_role('button', name='预约这台设备', exact=True).first.click()
            page.get_by_placeholder('如：底盘支架、外壳原型').fill('浏览器验收模型')
            page.get_by_role('button', name='确认预约', exact=True).click()
            page.get_by_role('button', name='我知道了', exact=True).wait_for()
            assert '5 分钟' in page.locator('.el-message-box').inner_text()
            page.get_by_role('button', name='我知道了', exact=True).click()
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
            if os.getenv('PRINTER_E2E_SID'):
                from datetime import datetime, timedelta, timezone
                start = (datetime.now(timezone(timedelta(hours=8))) + timedelta(hours=5)).replace(second=0, microsecond=0)
                end = start + timedelta(hours=1)
                form = page.locator('.add-booking-form')
                form.get_by_placeholder('已报名队伍的队长学号').fill(os.environ['PRINTER_E2E_SID'])
                form.locator('.el-select').click()
                page.get_by_role('option', name='拓竹 3 号机', exact=True).click()
                for label, value in [('选择开始时间', start), ('选择结束时间', end)]:
                    field = form.get_by_placeholder(label)
                    field.fill(value.strftime('%Y-%m-%d %H:%M'))
                    field.press('Enter')
                form.get_by_placeholder('填写用途').fill('管理员浏览器验收')
                page.get_by_role('button', name='直接添加预约', exact=True).click()
                page.get_by_text('预约已添加', exact=True).wait_for()
                card = page.locator('.admin-bookings article').filter(has_text='管理员浏览器验收').filter(has=page.get_by_role('button', name='删除预约', exact=True)).first
                card.get_by_role('button', name='删除预约', exact=True).click()
                page.get_by_role('button', name='确认删除', exact=True).click()
                page.get_by_text('预约已删除，历史已保留', exact=True).wait_for()
        if signup_href:
            page.evaluate('localStorage.setItem("selected_competition_event_id", "999999")')
            page.goto(args.url + signup_href, wait_until='networkidle')
            assert '拓竹' in page.locator('h1').inner_text(), 'Target event must override saved event'
        assert not errors, errors
        checks = ['three_printers', 'public_tabs', 'mobile_no_overflow', 'no_js_errors']
        if os.getenv('PRINTER_E2E_SID'):
            checks += ['captain_sid_only_identity', 'no_independent_password', 'create_booking', 'cancel_booking']
        if os.getenv('PRINTER_E2E_ADMIN'):
            checks += ['admin_identity', 'admin_page_three_printers', 'admin_direct_add_delete']
        checks += ['registration_targets_correct_event']
        print(json.dumps({'status': 'passed', 'checks': checks, 'screenshots': str(out)}, ensure_ascii=False))
        browser.close()


if __name__ == '__main__':
    main()
