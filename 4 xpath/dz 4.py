import requests
from lxml import html
import datetime
import re
import pandas as pd
from pymongo import MongoClient


def format_date(raw_date):
    month_dict = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
                  7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}

    if raw_date == 'Сегодня':
        now = datetime.datetime.now()
        date = f'{now.day} {month_dict[now.month]}'
    elif type(raw_date) == datetime.datetime:
        date = f'{raw_date.day} {month_dict[raw_date.month]}'
    else:
        date = raw_date
    return date


def format_name(raw_name):
    name = ''.join(raw_name)
    name = ''.join(re.findall(r'\w*\s\w*', name)).replace(u'\xa0', u' ')
    return name


header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}

# создаём пустой dataframe
news = {
    "name": [],
    "link": [],
    "date": [],
    "source": [],
}
news = pd.DataFrame(news)

# lenta.ru - тянем новости из рубрики Путешествия
lentalink = 'https://lenta.ru'
addlink = '/rubrics/travel/'
response = requests.get(f'{lentalink + addlink}', headers=header)

dom = html.fromstring(response.text)

articles = dom.xpath("//div[@class='item news b-tabloid__topic_news']")

for article in articles:
    name = article.xpath(".//h3//span/text()")
    name = format_name(name)

    link_rel = ''.join(article.xpath(".//h3//@href"))
    link = f'{lentalink + link_rel}'

    raw_date = ''.join(article.xpath("./div/span/text()"))
    date = format_date(raw_date)

    source = 'lenta.ru'

    # заполняем таблицу для новости
    add_news = pd.DataFrame({'name': [name],
                             'link': [link],
                             'date': [date],
                             'source': [source]
                             })
    # объединяем данные в одну таблицу
    news = pd.concat([news, add_news], axis=0)

# news.mail.ru - тянем новости из раздела Общество
maillink = 'https://news.mail.ru'
addlink = '/society/'
response = requests.get(f'{maillink + addlink}', headers=header)

dom = html.fromstring(response.text)

# выгрузим в 2 этапа - главная новость, затем секция Ранее

# обработаем главную новость дня
main_article_name = dom.xpath("//div[@class='js-module margin_top_20']//span[@class='newsitem__title-inner']/text()")
main_article_link = dom.xpath("//div[@class='js-module margin_top_20']//a[@class='newsitem__title link-holder']//@href")
raw_date = ''.join(dom.xpath("//div[@class='js-module margin_top_20']//div[@class='newsitem__params']//@datetime"))[:10]
raw_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")
format_date(raw_date)
main_article_date = format_date(raw_date)
main_article_source = dom.xpath(
    "//div[@class='js-module margin_top_20']//div[@class='newsitem__params']//span[last()]/text()")
main_add = pd.DataFrame({'name': [main_article_name],
                         'link': [main_article_link],
                         'date': [main_article_date],
                         'source': [main_article_source]
                         })
news = pd.concat([news, main_add], axis=0)

# список новостей сверху страницы обрабатывать не будем - нет даты и источника

# обработаем раздел Ранее
articles = dom.xpath("//div[@class='newsitem newsitem_height_fixed js-ago-wrapper js-pgng_item']")

for article in articles:
    name = article.xpath(".//span[@class='newsitem__title-inner']/text()")
    name = format_name(name)

    link = ''.join(article.xpath(".//a[@class='newsitem__title link-holder']//@href"))

    raw_date = ''.join(articles[1].xpath(".//div[@class='newsitem__params']//@datetime"))[:10]
    raw_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")
    date = format_date(raw_date)

    source = ''.join(article.xpath(".//span[@class='newsitem__param']//text()"))

    # заполняем таблицу для новости
    add_news = pd.DataFrame({'name': [name],
                             'link': [link],
                             'date': [date],
                             'source': [source]
                             })
    # объединяем данные в одну таблицу
    news = pd.concat([news, add_news], axis=0)

# yandex.news - тянем новости из раздела Главное
yandexlink = 'https://yandex.ru'
addlink = '/news'
response = requests.get(f'{yandexlink + addlink}', headers=header)

dom = html.fromstring(response.text)

articles = dom.xpath("//article")

for article in articles:
    name = article.xpath(".//a/h2/text()")
    name = format_name(name)

    link_rel = ''.join(article.xpath(".//a/h2/../@href"))
    link = f'{yandexlink + link_rel}'

    raw_date = 'Сегодня'
    date = format_date(raw_date)

    source = ''.join(article.xpath(".//span/a/text()"))

    # заполняем таблицу для вакансии
    add_news = pd.DataFrame({'name': [name],
                             'link': [link],
                             'date': [date],
                             'source': [source]
                             })
    # объединяем данные в одну таблицу
    news = pd.concat([news, add_news], axis=0)

# заливаем собранные данные в mongodb
client = MongoClient('localhost', 27017)
db = client['news']

news_db = db.parsed_news

news_for_upload = news.to_dict('records')

for line in news_for_upload:
    news_db.update_one(line, {'$set': line}, upsert=True)
