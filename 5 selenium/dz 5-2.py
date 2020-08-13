from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
from pymongo import MongoClient
import ast
import time

# запуск
chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome('./chromedriver', options=chrome_options)
driver.get('https://www.mvideo.ru/')

# закрываем всплывающее окно
close_btn = WebDriverWait(driver, 10).until(
    ec.presence_of_element_located((By.CLASS_NAME, 'tooltipster-close'))
)
close_btn.click()

# выбираем нужную карусель
carousels = driver.find_elements_by_xpath("//div[@data-init='ajax-category-carousel']")

for car in carousels:
    headers = car.find_elements_by_class_name('h2')

    for header in headers:
        if header.text == 'Хиты продаж':
            top_sellers = header.find_element_by_xpath("../../../div[@class='gallery-layout sel-hits-block ']")

# находим кнопку
next_btn = top_sellers.find_element_by_class_name('next-btn')

# вычисляем количество страниц
pages = len(top_sellers.find_element_by_class_name('carousel-paging').find_elements_by_tag_name('a'))

# создаём Dataframe
mvideo_top_sellers = {
    "name": [],
    "price": [],
    "link": []
}
mvideo_top_sellers = pd.DataFrame(mvideo_top_sellers)

# собираем данные
page = 1
products = top_sellers.find_elements_by_class_name('sel-product-tile-title')

while page <= pages:
    time.sleep(2)
    next_btn.click()
    page += 1

for product in products:
    data = product.get_attribute('data-product-info')
    data = ast.literal_eval(data)

    link = product.get_attribute('href')

    add_ts = pd.DataFrame({
        'name': [data['productName']],
        'price': [data['productPriceLocal']],
        'link': [link]
    })

    mvideo_top_sellers = pd.concat([mvideo_top_sellers, add_ts], axis=0)

driver.close()

# экспорт в БД
client = MongoClient('localhost', 27017)
db = client['mvideo']

mvideo_db = db.top_sellers

ts_to_upload = mvideo_top_sellers.to_dict('records')

for ts in ts_to_upload:
    mvideo_db.update_one(ts, {'$set': ts}, upsert=True)
