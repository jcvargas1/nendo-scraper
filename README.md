# nendo-scraper
Similar to my [other project](https://github.com/jcvargas1/chopshop-scraper), this is also another Python program that utilizes Scrapy web crawling framework to scrape the popular figure collection [Goodsmile.com](https://www.goodsmileus.com/index.php?route=common/home) in order to monitor when new products are released, when prices change, when items are in or out of stock, when preorder deadlines approach, and when items are removed from the site. Only the primary Python spider file is here for and does not include the PyEnv or Scrapy environments/files. 

## Why?

Similar to my other mentioned project, this was created to save my significant other time in having to constantly check the website to see when products were added or updated. In having this program she can now get notified immediately when there's any changes to the products and allows her to be able to obtain products that might otherwise be difficult to get due to low stock and popularity. In addition to this, I have also created a bot that allows the user to give it a link and the bot will calculate how much stock there is for that product. The only way to know the stock is by trial and error of inputting random amounts and basing the next guess based on the response the website gives you so the bot speeds up the process for the user immensely. By creating this program I have saved my significant other countless hours and allowed her to enjoy her hobby more. As well as create something that might be of use to other fellow hobbyists. 

## Tech Used

**Language/Libraries:** Python

**Services**: MongoDB Atlas (Cloud)

**Tools/Etc.** :  Scrapy, Selenium, XPath, Requests, PyMongo, Discord Py/API, Bash, PyEnv, Ubuntu (using my own physical server), VS Code

## How it works

The program is ran from Ubuntu server I have located at home. It consists of 2 separate spiders (an updater and creator) and a separate bot.A few times a day the program is triggered by a Cron job and begins scraping a specified starter link. Since the website does not have any API or obvious endpoint where one can get the data on the page such as in Json, everything has to be scraped via XPath. By using response and XPath I first get the total number of pages that there is so the program knows how many pages to traverse for scraping and it then proceeds to go through all the pages and checking the links of the products to see if they are located in the Mongo database. If the product is not in the database a function is called that proceeds to open the link and by using the correct XPaths I gather all the data needed to populate the objects fields. Once done it uploads to the database. Since new products are not added as frequently this spider is not ran as frequently as the other which is the updater spider. 

The updater spider/file runs every half hour and its job is to visit every single products (around 2000) links and see if the product has changed at all. Possible things that could change are the tags that consist of pre-order avilability, stock (in stock, sold out, almost sold out), and price. If any of the things the program monitors changes it proceeds to update the mongo database for that specific item as well as creating an embedded message with the relevant information and sending it to discord via a webhook. The reason this one runs more frequently is that this allows for being able to see if any high in demand products might go back in stock and they can be obtained before rapidly going back out of stock.

In order for the stock bot to work I had to use Selenium to run a headless firefox browser and emulate clicking buttons within the browser. Overall not the best experience so I would like to find a better way to implement this by possibly sending requests. 

## Demo Images
![Availability](https://github.com/jcvargas1/nendo-scraper/blob/main/nendo_ex_images/avail-ex.PNG)

![Latest](https://github.com/jcvargas1/nendo-scraper/blob/main/nendo_ex_images/latest-ex.PNG)

![Preorder1](https://github.com/jcvargas1/nendo-scraper/blob/main/nendo_ex_images/preorder-ex.PNG)

![Preorder2](https://github.com/jcvargas1/nendo-scraper/blob/main/nendo_ex_images/preorder-ex2.PNG)

![Stock](https://github.com/jcvargas1/nendo-scraper/blob/main/nendo_ex_images/stock-ex.PNG)
