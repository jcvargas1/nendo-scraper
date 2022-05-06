import sys
import os
import discord
from discord.ext import commands

from dotenv import load_dotenv

from os import link, sendfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time

import pymongo
from pymongo import MongoClient

# This is a discord bot that has a purpose of finding the stock of an item by emulating a browser and guessing the amount of stock.

cluster = MongoClient("insert mongo db info here")
db = cluster["nendo_scraper"]
load_dotenv()


TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

bot = commands.Bot(command_prefix='!')


@bot.command(name='stock', help='Responds with Nendo stock given link')
async def qtyFinder(ctx, *, link):
    options = Options()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("permissions.default.image", 2)
    driver = webdriver.Firefox(firefox_profile=profile)

    nendocollection = db["nendoroid_full"]
    await ctx.send("One moment.")

    if nendocollection.count_documents({"URL": link}) == 0:
        await ctx.send("Link given is not in database.")

    elif nendocollection.count_documents({"URL": link}) == 1:
        await ctx.send("Calculating Stock. . . !")
        nendo = nendocollection.find({"URL": {"$eq": link}})

        for item in nendo:
            if item["Availability"] == "Available Now":
                qtyDanger = ""
                while qtyDanger == "":
                    num1 = 300
                    link2 = item["URL"]
                    driver.get(link2)

                    element = driver.find_element_by_id(
                        "input-quantity").clear()
                    element = driver.find_element_by_id("input-quantity")
                    element.send_keys(str(num1))
                    time.sleep(3)
                    driver.find_element_by_xpath(
                        "//*[@id='button-cart']").click()
                    try:
                        qtyDanger = driver.find_element_by_xpath(
                            "//*[@id='product']/div[4]/div").text
                    except NoSuchElementException:
                        await ctx.send("Oh no the bot lost his count! He has to start over... one moment!")

                no_stock_phrase = "No enough quantity in stock"
                limit_phrase = "This item is only available (4) per customer."
                flag = False
                flag2 = False
                flag3 = False

                while flag3 != True:
                    try:
                        while flag != True:

                            if (num1 - 40) <= 0:
                                num1 -= 1
                                element = driver.find_element_by_id(
                                    "input-quantity").clear()
                                element = driver.find_element_by_id(
                                    "input-quantity")
                                element.send_keys(str(num1))
                                driver.find_element_by_xpath(
                                    "//*[@id='button-cart']").click()
                                try:
                                    qtyDanger = driver.find_element_by_xpath(
                                        "//*[@id='product']/div[4]/div").text

                                except NoSuchElementException:
                                    qtyDanger = ""

                                if qtyDanger != no_stock_phrase:
                                    flag = True

                            else:
                                num1 -= 40
                                element = driver.find_element_by_id(
                                    "input-quantity").clear()
                                element = driver.find_element_by_id(
                                    "input-quantity")
                                element.send_keys(str(num1))
                                driver.find_element_by_xpath(
                                    "//*[@id='button-cart']").click()
                                try:
                                    qtyDanger = driver.find_element_by_xpath(
                                        "//*[@id='product']/div[4]/div").text
                                except:
                                    qtyDanger = ""

                                if qtyDanger != no_stock_phrase:
                                    flag = True

                        while flag2 != True:

                            if qtyDanger == limit_phrase:
                                while qtyDanger != no_stock_phrase:
                                    num1 += 5
                                    element = driver.find_element_by_id(
                                        "input-quantity").clear()
                                    element = driver.find_element_by_id(
                                        "input-quantity")
                                    element.send_keys(str(num1))
                                    driver.find_element_by_xpath(
                                        "//*[@id='button-cart']").click()
                                    try:
                                        qtyDanger = driver.find_element_by_xpath(
                                            "//*[@id='product']/div[4]/div").text

                                    except NoSuchElementException:
                                        qtyDanger = ""

                                while qtyDanger == no_stock_phrase:
                                    num1 -= 1
                                    element = driver.find_element_by_id(
                                        "input-quantity").clear()
                                    element = driver.find_element_by_id(
                                        "input-quantity")
                                    element.send_keys(str(num1))
                                    driver.find_element_by_xpath(
                                        "//*[@id='button-cart']").click()
                                    qtyDanger = driver.find_element_by_xpath(
                                        "//*[@id='product']/div[4]/div").text

                            elif qtyDanger != no_stock_phrase or qtyDanger != limit_phrase:
                                delete_cart = driver.find_element_by_xpath(
                                    "//*[@id='con']/tbody/tr/td[3]/button").click()
                                num1 += 20
                                element = driver.find_element_by_id(
                                    "input-quantity").clear()
                                element = driver.find_element_by_id(
                                    "input-quantity")
                                element.send_keys(str(num1))
                                driver.find_element_by_xpath(
                                    "//*[@id='button-cart']").click()
                                qtyDanger = driver.find_element_by_xpath(
                                    "//*[@id='product']/div[4]/div").text

                                while qtyDanger == no_stock_phrase:
                                    num1 -= 1
                                    element = driver.find_element_by_id(
                                        "input-quantity").clear()
                                    element = driver.find_element_by_id(
                                        "input-quantity")
                                    element.send_keys(str(num1))
                                    driver.find_element_by_xpath(
                                        "//*[@id='button-cart']").click()
                                    try:
                                        qtyDanger = driver.find_element_by_xpath(
                                            "//*[@id='product']/div[4]/div").text
                                    except NoSuchElementException:
                                        qtyDanger = ""
                            flag2 = True
                        await ctx.send("**Given link:** " + link + "\n**STOCK: **" + str(num1 - 1))
                        nendocollection.update_one(
                            {"URL": link2}, {"$set": {"Stock": (num1 - 1)}})

                    except NoSuchElementException as exception:
                        pass
                    except ElementNotInteractableException as exception:
                        pass
                    flag3 = True
        driver.close()

bot.run(TOKEN)
