import scrapy
from scrapy.http import HtmlResponse
from dz_parser.items import DzParserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=менеджмент']

    def parse(self, response: HtmlResponse):
        book_links = response.css("a.book__image-link::attr(href)").extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
            next_page = response.xpath(
                "//a[@class='catalog-pagination__item _text js-pagination-catalog-item'][last()]/@href").extract_first()
            check_page = response.xpath(
                "//a[@class='catalog-pagination__item _text js-pagination-catalog-item'][last()]/text()").extract_first()
            if check_page == 'Далее':
                yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        link = response.url
        author = response.xpath("//span[@class='item-tab__chars-value']/a[1]/text()").extract_first()
        price_regular = response.xpath("//div[@class='item-actions__price-old']/text()").extract_first()
        price_discount = response.xpath("//div[@class='item-actions__price']/b/text()").extract_first()
        price_no_discount = response.xpath("//div[@class='item-actions__price']/b/text()").extract_first()
        rating = response.xpath("//span[@class='rating__rate-value']/text()").extract_first()
        yield DzParserItem(
            name=name,
            link=link,
            author=author,
            price_regular=price_regular,
            price_discount=price_discount,
            price_no_discount=price_no_discount,
            rating=rating
        )
