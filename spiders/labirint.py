import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%83%D1%88%D0%BA%D0%B8%D0%BD/?stype=0']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath(
            '//div[@class="product-cover"]//a[@class="cover"]/@href'
        ).extract()
        for link in range(len(book_links)):
            book_links[link] = 'https://www.labirint.ru'+book_links[link]
        for link in book_links:
            yield response.follow(link, callback=self.parse_books)

        next_page = response.xpath('//a[contains(@class, "pagination-next__text")]/@href').get()
        if next_page:
            yield  response.follow(next_page, callback=self.parse)
        print()
        pass
    def parse_books(self, response: HtmlResponse):
        link = response.xpath('//meta[@property="og:url"]/@content').get()
        title = response.xpath('//h1/text()').get()
        author = response.xpath(('//div[@class="authors"]/a[@class="analytics-click-js"]/text()')).get()
        price = response.xpath('//div[@class="buying-priceold"]//span[@class="buying-priceold-val-number"]/text()').get()
        price_new = response.xpath('//div[@class="buying-pricenew"]//span[@class="buying-pricenew-val-number"]/text()').get()
        if price == None and price_new == None:
            price = response.xpath('//div[@class="buying-price"]//span[@class="buying-price-val-number"]/text()').get()
            price_new = response.xpath('//div[@class="buying-price"]//span[@class="buying-price-val-number"]/text()').get()

        rating = response.xpath('//div[contains(@id, "product-voting-body")]//div[@id="rate"]/text()').get()
        print('')
        yield BookparserItem(link=link, title=title, author=author, price=price, price_new=price_new, rating=rating)