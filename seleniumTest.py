from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

driver = webdriver.Firefox()

driver.get('https://www.bbc.com')

button = driver.find_element(By.CLASS_NAME, "sc-49542412-3")
button.click()

search_bar = driver.find_element(By.CLASS_NAME, "sc-e1a87ea7-1")
search_button = driver.find_element(By.CLASS_NAME, "sc-c3b248c2-0")

search_bar.send_keys("China")
search_button.click()

advertise_close = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "close-button"))
)
advertise_close.click()

soup = BeautifulSoup(driver.page_source, 'html5lib')
news_link_div = soup.select('.iIDZOJ')
# print(test)
for i in news_link_div:
    print(i.div.div.a)

# for i in news_link_div:
    # print(i.find('a', class_='jZSdZm').href)

# search_bar = driver.find_element(By.CLASS_NAME, "hjcTEu")
# search_bar.clear()
# search_bar.send_keys("Russia")

# second_search_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div[1]/div/div[1]/button[2]")
# second_search_button.click()

