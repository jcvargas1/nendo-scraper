from urllib.request import Request
import pymongo
from pymongo import MongoClient
from datetime import datetime
import scrapy
import requests
from discord import Webhook, RequestsWebhookAdapter, Embed
from scrapy.crawler import CrawlerProcess
from scrapy import Request

cluster = MongoClient("insert mongo db info here")
db = cluster["nendo_scraper"]
linkcollection = db["nendo_links"]
linkcollection.drop()
linkcollection = db["nendo_links"]


class NendoroidsSpider(scrapy.Spider):
    name = 'nendoroids'
    allowed_domains = ['goodsmileus.com']
    start_urls = [
        'https://www.goodsmileus.com/category/figures-67/nendoroid-268']

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        for url in self.start_urls:
            yield Request(url, headers=headers)

    def parse(self, response):

        # Get specific data from the page using scrapy
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        nendo_link = response.xpath('//*[@id="content"]//h4/a/@href').extract()
        for url in nendo_link:
            yield scrapy.Request(url, self.checklinks, headers=headers)

            # Iterates through all pages

            next_page = response.css('link[rel=next]::attr(href)').get()
            if next_page:
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse, headers=headers)

    # Creates entry into nendoroid_full collection

    def createNendo(self, response):
        nendocollection = db["nendoroid_full"]

        nendo_name = response.xpath(
            '//*[@id="content"]/div/div/div[2]/div[1]/h1/text()').get()
        nendo_link = response.url
        nendo_price = response.xpath(
            '//*[@id="product"]/ul[2]/li[1]/text()').get()
        nendo_series = response.xpath(
            '//*[@id="product"]//span[@class="tag-black"]/text()').get()
        nendo_tag = response.xpath(
            '//*[@id="product"]//span[@class="tag-green"]/text()| //*[@id="product"]//span[@class="tag-orange"]/text() | //*[@id="product"]//span[@class="tag-grey"]/text() | //*[@id="product"]//span[@class="tag-red"]/text()').extract()
        nendo_image = response.xpath('//*[@id="image"]/@src').get()
        nendo_new = ""
        nendo_avail = ""
        nendo_pre_bonus = "None"
        nendo_stock = 0

        if nendo_price == "":
            nendo_price = response.xpath(
                '//*[@id="product"]/ul[2]/li[3]/text()').get()

        for item in nendo_tag:
            if item == "New":
                nendo_new = "New"
            elif item == "Pre-Order":
                nendo_avail = "Available for Pre-Order"
            elif item == "Pre-Order Bonus":
                nendo_pre_bonus = "Yes"
            elif item == "Sold Out":
                nendo_avail = "Sold Out"
            elif item == "Almost Sold Out":
                nendo_avail = "Almost Sold Out"
            elif item == "Available Now":
                nendo_avail = "Available Now"
            elif item == "Pre-Order Closed":
                nendo_avail == "Pre-Order Closed"

        nendocollection.insert_one({"Name": nendo_name, "URL": nendo_link, "Price": nendo_price, "Series": nendo_series, "Status": nendo_new,
                                    "Pre-Order Bonus": nendo_pre_bonus, "Availability": nendo_avail, "Image": nendo_image, "Stock": nendo_stock})

        discRelease = "insert you discord webhook link here"

        webhook = Webhook.from_url(
            discRelease, adapter=RequestsWebhookAdapter())

        print("ADDED NEW ITEM TO nendoroid_full DB: \n**Name**: " + nendo_name + "\n**Series**: " + nendo_series + "\n**Status**: " + nendo_avail + "\n**Pre-Order Bonus**: " + nendo_pre_bonus
              + "\n**Price**: " + nendo_price + "\nCurrent Stock: " + str(nendo_stock) + "\n**Link**: " + nendo_link)

        embed_new = Embed(title="**New Item Added!**", color=0x70ACC3,
                          description=f"[{nendo_name}]({nendo_link})")
        embed_new.add_field(name="Series\n", value=nendo_series)
        embed_new.add_field(name="Status\n", value=nendo_avail)
        embed_new.add_field(name="Pre-Order Bonus\n", value=nendo_pre_bonus)
        embed_new.add_field(name="Price\n", value=nendo_price)
        embed_new.set_image(url=nendo_image)
        webhook.send(embed=embed_new)

    # Checks all links to see if there and if not inserts links to nendo_links collection
    def checklinks(self, response):

        linkcollection = db["nendo_links"]
        link = response.url
        nendocollection = db["nendoroid_full"]
        link = response.url
        if nendocollection.count_documents({"URL": link}) == 0:
            print(link + " IS NOT IN CURRENT DB. PROCEEDING TO ADD")
            self.createNendo(response)
        linkcollection.insert_one({"link": link})


process = CrawlerProcess()
process.crawl(NendoroidsSpider)
process.start()
