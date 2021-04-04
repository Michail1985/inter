import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%BF%D1%83%D1%88%D0%BA%D0%B8%D0%BD']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath(
            '//div[@class="catalog-products__item"]//a[@class="book-preview__image-link"]/@href'
        ).extract()
        for link in book_links:
            yield response.follow(link, callback=self.parse_books)

        next_page = response.xpath(
            '//div[@class="catalog-pagination__list"]'
            '//a[contains(@class, "catalog-pagination__item _text")]/@href'
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        print()

    def parse_books(self, response: HtmlResponse):
        link = response.xpath('//link[@rel="amphtml"]/@href').get()
        link = link.replace("/amp/", "/")
        title = response.xpath('//h1[@itemprop="name"]/text()[1]').get()
        title = ' '.join(title.split())
        author = response.xpath(('//div[@class="item-tab__chars-item"]//a/text()')).get()
        price = response.xpath('//div[@class="item-actions__price-old"]/text()').get()
        #if price.find("р.") != -1:
        #    price = price.replace(" р.", "")
        price_new = response.xpath('//div[@class="item-actions__price"]/b[@itemprop="price"]/text()').get()
        rating = response.xpath('//div[@class="live-lib__rate-value"]').get()
        if price == None:
            price = response.xpath('//div[@class="item-actions__price"]/b[@itemprop="price"]/text()').get()
        print('')
        yield BookparserItem(link=link, title=title, author=author, price=price, price_new=price_new, rating=rating)
