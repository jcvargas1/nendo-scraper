# Iterates through MongoDB list of links and checks if the nendos in the DBs data are updated

from pymongo import MongoClient
from discord import Webhook, RequestsWebhookAdapter, Embed

import requests
import scrapy
import pymongo
from scrapy.crawler import CrawlerProcess
import discord
from scrapy import Request

cluster = MongoClient("insert mongo db info here")
db = cluster["nendo_scraper"]


class NendoUpdaterSpider(scrapy.Spider):
    name = 'nendo_updater'
    allowed_domains = ['goodsmileus.com']
    start_urls = [
        'https://www.goodsmileus.com/category/Figures-67/nendoroid-268']

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/FD537.36'}
        for url in self.start_urls:
            yield Request(url, headers=headers)

    def parse(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        linkcollection = db["nendo_links"]
        results = linkcollection.find({})
        for item in results:
            yield scrapy.Request(item["link"], self.update_nendos, headers=headers)
            print("Working on link: " + item["link"])

    def removed_links():
        linkcollection = db["nendo_links"]
        nendocol = db["nendoroid_full"]
        nendocol_links = nendocol.find({})
        nendo_deleted = db["deleted_nendos"]
        discRemoved = "insert you discord webhook link here"

        # Compares nendo collection in the db and if its not in the updated
        # nendo_links anymore then it deletes the object and copies data to deleted_nendos
        for item in nendocol_links:
            if linkcollection.count_documents({"link": item["URL"]}) == 0 and nendo_deleted.count_documents({"URL": item["URL"]}) == 0:
                nendo_deleted.insert_one({"Name": item["Name"], "URL": item["URL"], "Price": item["Price"], "Series": item["Series"],
                                          "Status": item["Status"], "Pre-Order Bonus": item["Pre-Order Bonus"], "Availability": item["Availability"], "Image": item["Image"]})
                webhook = Webhook.from_url(
                    discRemoved, adapter=RequestsWebhookAdapter())
                webhook.send("------------------------------------------------------"+item["Image"] + "\n**Name**: " + item["Name"] + "\n**Series**: " + str(
                    item["Series"]) + "\n**Status**: " + item["Status"] + "\n**Pre-Order Bonus**: " + item["Pre-Order Bonus"] + "\n**Price**: " + item["Price"] + "\n**Link**: <" + item["URL"] + ">")
                nendocol.delete_one({"URL": item["URL"]})

    def update_nendos(self, response):

        update_url = response.url
        nendocol = db["nendoroid_full"]

        nendosearch = nendocol.find({"URL": {"$eq": update_url}})

        nendo_price = response.xpath(
            '//*[@id="product"]/ul[2]/li[1]/text()').get()
        nendo_tag = response.xpath(
            '//*[@id="product"]//span[@class="tag-green"]/text()| //*[@id="product"]//span[@class="tag-orange"]/text() | //*[@id="product"]//span[@class="tag-grey"]/text() | //*[@id="product"]//span[@class="tag-red"]/text()').extract()

        nendo_new = ""
        nendo_avail = ""

        discUpdate = "insert you discord webhook link here"

        webhook = Webhook.from_url(
            discUpdate, adapter=RequestsWebhookAdapter())

        discUpdate2 = "insert you discord webhook link here"
        webhook2 = Webhook.from_url(
            discUpdate2, adapter=RequestsWebhookAdapter())

        flag1 = False

        for item in nendo_tag:
            if item == "New":
                nendo_new = "New"
            elif item == "Pre-Order":
                nendo_avail = "Available for Pre-Order"
            elif item == "Sold Out":
                nendo_avail = "Sold Out"
            elif item == "Available Now":
                nendo_avail = "Available Now"
            elif item == "Almost Sold Out":
                nendo_avail = "Almost Sold Out"
            elif item == "Pre-Order Closing":
                preorder_close_date = "Pre-Order Closing"
                flag1 = True
                preorder_close_date = response.xpath(
                    '//*[@id="product"]//li[3]/span/text()').get()
            elif item == "Pre-Order Closed":
                nendo_avail = "Pre-Order Closed"

        for item in nendosearch:
            dbPrice = item["Price"]
            dbPrice = float(dbPrice.replace("$", ""))
            nendo_price_cent = float(nendo_price.replace("$", ""))

            nendoName = item["Name"]
            nendoLink = str(item["URL"])

            if item["Price"] != nendo_price and nendo_price != "None" and (nendo_price_cent != (dbPrice + 0.01)):

                nendoOldPrice = str(item["Price"])

                embed_new = Embed(title="Price Change!", color=0x70ACC3,
                                  description=f"[{nendoName}]({nendoLink})")
                embed_new.add_field(name="Old Price\n",
                                    value=str(nendoOldPrice))
                embed_new.add_field(name="New Price\n", value=str(nendo_price))
                embed_new.set_image(url=item["Image"])
                webhook2.send(embed=embed_new)

                nendocol.update_one({"URL": update_url}, {
                                    "$set": {"Price": nendo_price}})
                print("UPDATING " + item["Name"] + " PRICE")

            if item["Status"] != nendo_new:
                nendocol.update_one({"URL": update_url}, {
                                    "$set": {"Status": nendo_new}})
                print("UPDATING " + item["Name"] + " STATUS")
            if item["Availability"] != nendo_avail and nendo_avail != "":

                oldAvail = str(item["Availability"])

                embed_new = Embed(title="Status Change!", color=0x70ACC3,
                                  description=f"[{nendoName}]({nendoLink})")
                embed_new.add_field(
                    name="Availability\n", value=f"Availability: {oldAvail} ---> {nendo_avail}")
                embed_new.add_field(name="New Price\n", value=str(nendo_price))
                embed_new.set_image(url=item["Image"])
                webhook.send(embed=embed_new)

                nendocol.update_one({"URL": update_url}, {
                                    "$set": {"Availability": nendo_avail}})

                print("\n\n\nUPDATING " + item["Name"] + " AVAILABILITY")
            if flag1 == True and nendocol.count_documents({"URL": update_url, "Pre-Order_Closing": {"$exists": False}}) == 1:

                embed_new = Embed(title="Status Change!", color=0x70ACC3,
                                  description=f"[{nendoName}]({nendoLink})")
                embed_new.add_field(
                    name="Pre-Order Closing\n", value=f"Close Date: {str(preorder_close_date)}")
                embed_new.set_image(url=item["Image"])
                webhook.send(embed=embed_new)

                nendocol.update_one({"URL": update_url}, {
                                    "$set": {"Pre-Order_Closing": preorder_close_date}})

    removed_links()


process = CrawlerProcess()
process.crawl(NendoUpdaterSpider)
process.start()
