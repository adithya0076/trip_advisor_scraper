import traceback

import bs4
import pandas as pd
import re
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TripAdvisorAttractionsScraper:

    def __init__(self, obj, db):
        self.selenium_helper = obj
        self.db = db

    def search_for_attractions(self, driver, city):
        """
        This function opens the Thing's to do page from the home screen and the search for the city.

        Args:
            driver (Geckodriver): The driver where the url is opened.
            city: The city to which to be searched.
        :param driver:
        :param city:
        :return:
        """

        # Finds the Restaurant's page button
        status, things = self.selenium_helper.find_xpath_element(
            driver=driver, xpath="//a[@href='/Attractions']",
            is_get_text=False
        )
        things.click()
        WebDriverWait(driver, 5)
        self.selenium_helper.sleep(random.randint(5, 8))
        # Finds the input
        status, search = self.selenium_helper.find_xpath_element(
            driver=driver,
            xpath="//div[@class='kaEuY']//input[@placeholder='Where to?']",
            is_get_text=False
        )
        search.send_keys(city)
        WebDriverWait(driver, 10)
        self.selenium_helper.sleep(random.randint(5, 10))
        search.send_keys(Keys.ENTER)
        print(f"The city: '{city}' is searched")
        #

    def scrape_attraction_data(self, driver, city):
        """
        This function is using bs4 to scrape current page source for hotels.

        Args:
            driver (Geckodriver): The driver where the url is opened.
            city: The city name.

        Returns:
            The pandas dataframe which the scraped data are saved into.
        :param driver:
        :param city:
        :return df:
        """
        status, ad = self.selenium_helper.find_xpath_element(
            driver=driver, xpath="//div[@class='UsGfI I']//button", is_get_text=False
        )

        try:
            ad.click()
        except:
            print("No ad")

        self.selenium_helper.sleep(5)

        status, see_all = self.selenium_helper.find_xpath_element(
            driver=driver, xpath="//div[@class='BYvbL A YeunF']//div[@class='Fofmq']/a",

        )

        try:
            see_all.click()
        except:
            print("No see all")

        self.selenium_helper.sleep(random.randint(5, 10))

        # Gets the current source page
        source = driver.page_source
        print(f"SOURCE is loaded")

        # Use bs4 to parse data from the source
        data = bs4.BeautifulSoup(source, 'lxml')

        self.selenium_helper.sleep(random.randint(5, 10))

        # Selects the elements
        attractions = data.select(".VLKGO")

        urls = []

        # Saving the urls of Restaurants available
        for i in attractions:
            a = i.find('a')
            if a.is_empty_element:
                print('None')
            else:
                link = 'https://www.tripadvisor.com/' + a['href'] + ''
                urls.append(link)

        # Checking whether next button is available
        wait = WebDriverWait(driver, 10)
        self.selenium_helper.sleep(random.randint(5, 10))

        a = 1
        while a:
            try:
                self.selenium_helper.sleep(random.randint(5, 10))
                # scroll
                self.selenium_helper.driver_execute(
                    driver=driver, program="window.scrollTo(0, document.body.scrollHeight);"
                )

                status, btnNext = self.selenium_helper.find_xpath_element(
                    driver=driver,
                    xpath="//div[@class='UCacc']//a[@data-smoke-attr='pagination-next-arrow']",
                    is_get_text=False
                )

                btnNext.click()
                # element.click()
                self.selenium_helper.sleep(random.randint(5, 10))

                # Gets the current SOURCE
                source = driver.page_source
                print(f"URL is loaded")

                # Use bs4 to parse data from the URL
                data = bs4.BeautifulSoup(source, 'lxml')

                # Selects the elements
                attractions = data.select(".VLKGO")

                self.selenium_helper.sleep(random.randint(5, 10))

                for i in attractions:
                    a = i.find('a')
                    if a.is_empty_element:
                        print('None')
                    else:
                        link = 'https://www.tripadvisor.com/' + a['href'] + ''
                        urls.append(link)
            except Exception as e:
                print(e)
                break
        print(urls)