import asyncio
from playwright.async_api import async_playwright
import datetime

async def main():

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://ispace-lis.nsysu.edu.tw/manager/loginmgr.aspx')

        # fill in the form
        id = page.get_by_placeholder('請輸入系統登入帳號')
        pw = page.get_by_placeholder('請輸入系統登入密碼')

        await id.fill('ispaceAdmin')
        await pw.fill('space@LIS#2426')

        captcha = page.get_by_placeholder('請輸入認證文字')
        vc = input("Verification code: ")
        await captcha.fill(vc)

        login_button = page.get_by_title('登 入')
        await login_button.click()
        await page.wait_for_timeout(2000)
        
        
        # Setting
        await page.frame_locator('#mainframe').get_by_title('空間管理').click()
        await page.frame_locator('#subframe').get_by_title('小型討論室').click()
        await page.frame_locator('#subframe').get_by_title('討論室暫停使用列表').first.click()

        start_date = input("Start date (YYYY/MM/DD): ")
        end_date = input("End date (YYYY/MM/DD): ")

        date_1 = datetime.datetime.strptime(start_date,'%Y/%m/%d')
        date_2 = datetime.datetime.strptime(end_date,'%Y/%m/%d')

        interval = abs(date_2 - date_1).days

        for i in range(interval):
            await page.frame_locator('#contentframe').frame_locator('#iframePage').get_by_title('新增暫停使用空間').click()
            await page.frame_locator('#contentframe').locator('#floor').select_option('圖書館1F')
            await page.wait_for_timeout(2000)
            await page.frame_locator('#contentframe').locator('label.chkboxAll').set_checked(True)
            await page.wait_for_timeout(2000)
            await page.frame_locator('#contentframe').locator('input.YYYYMMDD').click()
            await page.wait_for_timeout(2000)
            await page.frame_locator('#contentframe').get_by_title(date_1.strftime('%Y/%m/%d')).click()
            await page.wait_for_timeout(2000)
            await page.frame_locator('#contentframe').get_by_text('23:30~23:59').click()
            await page.wait_for_timeout(2000)
            await page.frame_locator('#contentframe').locator('div.pagefun').nth(0).get_by_title('新增暫停使用空間').click()
            await page.wait_for_timeout(2000)

            date_1 = date_1 + datetime.timedelta(days=1)

        

        await page.wait_for_timeout(50000)



        await browser.close()

asyncio.run(main())