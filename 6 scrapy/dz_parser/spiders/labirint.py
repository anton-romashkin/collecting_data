import scrapy
from scrapy.http import HtmlResponse
from dz_parser.items import DzParserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/Музыка/?stype=0']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath("//a[@class='cover']/@href").extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
            next_page = response.xpath(
                "//div[@class='pagination-next pagination-next-mobile']//a/@href").extract_first()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        link = response.url
        author = response.xpath("//a[@data-event-label='author']/text()").extract_first()
        price_regular = response.xpath("//span[@class='buying-priceold-val-number']/text()").extract_first()
        price_discount = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract_first()
        price_no_discount = response.xpath("//span[@class='buying-price-val-number']/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()
        yield DzParserItem(
            name=name,
            link=link,
            author=author,
            price_regular=price_regular,
            price_discount=price_discount,
            price_no_discount=price_no_discount,
            rating=rating
        )
