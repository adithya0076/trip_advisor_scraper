import selenium
import io
import requests
import bs4
import urllib.request
import urllib.parse
import pandas as pd
from selenium import webdriver

import time

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options


# PATHS
SCRAPING_URL = "https://www.tripadvisor.com"
GECKO_DRIVER_PATH = "driver/geckodriver.exe"

class TripAdvisorScraper:
    def __init__(self):
        self.SCRAPING_URL = "https://www.tripadvisor.com"
        self.GECKO_DRIVER_PATH = "driver/geckodriver.exe"

    def get_driver(self):
        """

        Creating and returning the selenium webdriver.

        Uses firefox and the geckodriver.
        :return driver_object:

        Returns:
             Geckodriver object: This driver object is used to simulate the firefox browser.
        """

        # Creating the service object to pass the executable geckodriver path to webdriver
        service_obj = Service(executable_path=GECKO_DRIVER_PATH)
        profile_path = r'C:\Users\sinxdell\AppData\Roaming\Mozilla\Firefox\Profiles\2lfh6wg7.default-release'
        # Creating the Firefox options to add the additional options to the webdriver
        options = Options()

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('ignore-ssl-errors')
        options.set_preference('profile', profile_path)
        driver = Firefox(options=options, service=service_obj)
        driver.maximize_window()
        print('Webdriver is created')
        return driver

    def get_driver_object(self, driver=get_driver(), url=SCRAPING_URL):
        """
        This function will get the driver object and url as parameters and opens the given URL.

        Args:
            driver (Geckodriver): _description_. Defaults to get_driver().
            url (str, optional): URL of the website. Defaults to SCRAPING_URL.

        Returns:
            Geckodriver: The driver where the given url is opened.

        :param driver:
        :param url:
        :return driver:

        """

        # opening the URL
        driver.get(url)
        print(f"The URL '{url}' is opened ")
        return driver

    def search_for_hotels(self, driver, city):
        """
        This function opens the hotels page from the home screen and the search for the city.

        Args:
            driver (Geckodriver): The driver where the url is opened.
            city: The city to which to be searched.
        :param driver:
        :param city:

        """
        # Finds the hotel page button
        driver.find_element(by=By.XPATH, value="//a[@href='/Hotels']").click()

        l = driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/form/input[1]")
        l.send_keys(city)
        WebDriverWait(driver, 10)
        time.sleep(5)
        l.send_keys(Keys.ENTER)
        print(f"The city: '{city}' is searched")

    def scraping_hotels_data(self, driver, city):
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

        # Gets the current URL
        url = driver.page_source
        print(f"URL is loaded")

        # Use bs4 to parse data from the URL
        data = bs4.BeautifulSoup(url, 'lxml')

        # Elements which are selected
        read1 = data.select(".listing_title")
        read2 = data.select(".price-wrap")

        name = []
        for i in range(len(read1)):
            x = read1[i].text
            x = x.lstrip()
            name.append(x)
        print(name)

        price = []
        for i in read2:
            x = i.text
            x = x.replace("LKR", " ")
            x = x.lstrip()
            x = x.split(" ")
            if (len(x) > 1):
                price.append(str(x[1]))
            else:
                price.append(str(x[0]))
        print(price)

        # Creating a dictionary to send it to the dataframe

        dict = {'city': city, 'hotel': name, 'price': price}
        df = pd.DataFrame(dict)
        df.style.set_table_attributes("style='display:inline'").set_caption(city)

        return df

    def write_to_csv(self,data):
        """
        Writes the pandas dataframe into a csv file in file directory.

        Args:
            data (Pandas DataFrame): The driver where the url is opened.

        :param data:

        """

        # Writing data into a csv
        if data is None:
            print('No Data Recorded')
        else:
            data.to_csv("hotels_list.csv", mode='a', header=True)


obj = TripAdvisorScraper()

driver = obj.get_driver_object()
df = pd.read_csv("datasets/cities.csv")
for index, row in df.iterrows():
    # print(row['name_en'])

    # Create the driver

    time.sleep(5)

    # Searching for hotels
    obj.search_for_hotels(driver=driver, city=row['name_en'])
    time.sleep(10)

    # Scraping the hotels data
    data = obj.scraping_hotels_data(driver, city=row['name_en'])
    print(data)

    if data.empty is True:
        print("No data")
    else:
        # Writes the dataframe into a csv
        obj.write_to_csv(data)

    time.sleep(10)
    driver.get(SCRAPING_URL)
    if index == 5:
        break
driver.quit()