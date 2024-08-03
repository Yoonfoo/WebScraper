from pymongo import MongoClient
import asyncio
from time import sleep
from playwright.async_api import async_playwright

async def main():

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://www.bbc.com')
        await page.get_by_label('Search BBC').click()
        await page.get_by_placeholder('Search news, topics and more').fill('China')
        await page.get_by_test_id("search-input-search-button").click()
        
        page_num = 1
        client = MongoClient('mongodb://localhost:27017/')
        news_db = client.news_db
        news_list = news_db.news_list

        sleep(3)

        next_button = await page.get_by_test_id('pagination-next-button').all()

        while(await next_button[0].is_enabled()):
            print(f"""
                    Page {page_num}
                """)

            height = await page.evaluate("""() => {
                const height = document.body.scrollHeight;
                return height                    
            }""")

            await page.mouse.wheel(0, height)

            internal_links = await page.get_by_test_id('liverpool-card').locator('> div').locator('> a').all()
            headings = await page.get_by_test_id('card-headline').all()
            news_imgs = await page.get_by_test_id('card-media').locator('> div').locator('> img').all()
            descriptions = await page.get_by_test_id('card-description').all()

            scraped_news = []

            for heading, description, internal_link, news_img in zip(
                headings, 
                descriptions,
                internal_links,
                news_imgs 
            ):       

                heading_text = await heading.text_content()
                description_text = await description.text_content()
                internal_link_text = await internal_link.get_attribute('href')
                internal_link_text = internal_link_text.replace('https://www.bbc.com','')
                news_img_text = await news_img.get_attribute('src')

                news_data = {
                    'title': heading_text,
                    'description': description_text,
                    'news_link': 'https://www.bbc.com' + internal_link_text,
                    'news_image': news_img_text,
                }

                scraped_news.append(news_data)

                print(f"""
                    Title: {heading_text}
                    Description: {description_text}
                    Link: https://www.bbc.com{internal_link_text}                  
                    Image Link: {news_img_text}
                    """)

            result = news_list.insert_many(scraped_news)

            await next_button[0].click()
            await page.mouse.wheel(0, -height)

            page_num += 1
            sleep(3)

        await browser.close()
        client.close()

asyncio.run(main())