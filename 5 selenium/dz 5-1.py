from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import pandas as pd
import time

# запуск
chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome('./chromedriver', options=chrome_options)
driver.get('https://mail.ru/')

# авторизация
login = driver.find_element_by_id('mailbox:login')
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)

password = WebDriverWait(driver, 10).until(
    ec.element_to_be_clickable((By.ID, 'mailbox:password'))
)
password.send_keys('NextPassword172')
password.send_keys(Keys.ENTER)

# собираем ссылки на письма
mail_set = set()
while True:
    time.sleep(2)
    collected_before = len(mail_set)
    mails = driver.find_elements_by_class_name('js-letter-list-item')

    for item in mails:
        mail_set.add(item.get_attribute('href'))

    collected_after = len(mail_set)

    if collected_after > collected_before:
        action = ActionChains(driver)
        action.move_to_element(mails[-1])
        action.perform()
    else:
        break

# создаём пустой Dataframe
mails = {
    "sender": [],
    "date": [],
    "subject": [],
    "mail_text": [],
}
mails = pd.DataFrame(mails)

# собираем данные из писем
for mail in mail_set:
    driver.get(mail)

    sender = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'letter-contact'))
    ).get_attribute('title')

    date = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'letter__date'))
    ).text

    subject = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.TAG_NAME, 'h2'))
    ).text

    mail_text = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'letter__body'))
    ).text

    add_mail = pd.DataFrame({'sender': [sender],
                             'date': [date],
                             'subject': [subject],
                             'mail_text': [mail_text]
                             })

    mails = pd.concat([mails, add_mail], axis=0)

driver.close()

# экспорт в Mongodb
client = MongoClient('localhost', 27017)
db = client['mail']
mail_db = db.parsed_mail

mail_for_upload = mails.to_dict('records')
for mail in mail_for_upload:
    mail_db.update_one(mail, {'$set': mail}, upsert=True)
