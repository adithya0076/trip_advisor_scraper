import json
import bs4
import pandas as pd
import re
import time
import traceback
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from mysql.connector import Error


# from ..dbModel.BaseDb import BaseDB


class TripAdvisorRestaurantScraper:

    def __init__(self):
        self.GECKO_DRIVER_PATH = "../driver/geckodriver.exe"
        self.SCRAPING_URL = "https://www.tripadvisor.com"

        # Creating the service object to pass the executable geckodriver path to webdriver
        self.service_obj = Service(executable_path=self.GECKO_DRIVER_PATH)
        self.profile_path = r'C:\Users\sinxdell\AppData\Roaming\Mozilla\Firefox\Profiles\2lfh6wg7.default-release'

        # Creating the Firefox options to add the additional options to the webdriver
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('ignore-ssl-errors')
        self.options.set_preference('profile', self.profile_path)

    def getdriver(self):
        """
         Creating and returning the selenium webdriver.

         Uses firefox and the geckodriver.


        Returns:
         Geckodriver object: This driver object is used to simulate the firefox browser.
        :return driver_object:
        """

        driver = Firefox(options=self.options, service=self.service_obj)
        driver.maximize_window()
        print('-------------------------------Webdriver is created-------------------------------')
        driver.get(self.SCRAPING_URL)
        print(f"The URL '{self.SCRAPING_URL}' is opened ")

        return driver

    def search_for_restaurants(self, driver, city):
        """
        This function opens the Restaurant's page from the home screen and the search for the city.

        Args:
            driver (Geckodriver): The driver where the url is opened.
            city: The city to which to be searched.
        :param driver:
        :param city:
        :return:
        """

        # Finds the Restaurant's page button
        driver.find_element(by=By.XPATH, value="//a[@href='/Restaurants']").click()
        WebDriverWait(driver, 10)
        time.sleep(10)
        # Finds the input
        search = driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/form/input[1]")

        search.send_keys(city)
        WebDriverWait(driver, 10)
        time.sleep(5)
        search.send_keys(Keys.ENTER)
        print(f"The city: '{city}' is searched")

    def scrape_restaurant_data(self, driver, city):
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

        # Selects the elements
        restaurants = data.select(".RfBGI")

        urls = []

        # Saving the urls of Restaurants available
        for i in restaurants:
            a = i.find('a')
            if a.is_empty_element:
                print('None')
            else:
                link = 'https://www.tripadvisor.com/' + a['href'] + ''
                urls.append(link)

        # Checking whether next button is available
        wait = WebDriverWait(driver, 10)
        time.sleep(15)

        a = 1
        while a:
            print("Clicked")
            try:
                # element = wait.until(EC.element_to_be_clickable(
                #     (By.XPATH, "//a[@class='ui_button next primary']")))
                # print("clickable")
                time.sleep(10)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # time.sleep(6)
                try:

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='BrOJk u j z _F wSSLS HuPlH Vonfv']"))).click()
                except:
                    pass
                # time.sleep(5)
                # element = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, "//a[@class='ui_button next primary']")))

                driver.find_element(by=By.XPATH, value="//a[@class='nav next rndBtn ui_button primary taLnk']").click()
                # element.click()
                time.sleep(10)

                # Gets the current URL
                url = driver.page_source
                print(f"URL is loaded")

                # Use bs4 to parse data from the URL
                data = bs4.BeautifulSoup(url, 'lxml')

                # Selects the elements
                restaurants = data.select(".RfBGI")

                time.sleep(5)

                for i in restaurants:
                    a = i.find('a')
                    if a.is_empty_element:
                        print('None')
                    else:
                        link = 'https://www.tripadvisor.com/' + a['href'] + ''
                        urls.append(link)


            except Exception as e:
                print(e)
                break

        dict2 = {'city': city, 'url': urls, }
        fd = pd.DataFrame(dict2)
        print('Dataset for URLs', fd)

        return fd

    def scraping_restaurant_information(self, driver, data):
        """
        Scrape the Details about each restaurant from iterating through the links

        :param driver:
        :param data:
        :return:
        """
        driver2 = driver
        name = []
        review_count = []
        address = []
        contact = []
        description = []
        website = []
        hotel = []
        geocodes = []
        price_range = []
        cuisines = []
        meals = []
        features = []
        email = []

        for index, row in data.iterrows():
            images = []

            driver2.get(row['url'])
            time.sleep(10)

            # Load the url
            url = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(url, 'lxml')
            WebDriverWait(driver2, 10)

            # Elements which are selected
            name_sc = data2.select(".HjBfq")
            reviews_sc = data2.select(".AfQtZ")
            address_sc = driver2.find_element(by=By.XPATH, value="/html/body/div[2]/div[1]/div/div[4]/div/div/div[3]/span[1]/span/a").text
            contact_sc = driver2.find_element(by=By.XPATH, value="/html/body/div[2]/div[1]/div/div[4]/div/div/div[3]/span[2]/span/span[2]/a").text
            email_sc = data2.select(".IdiaP.Me.sNsFa")
            websiteurl_sc = driver2.find_element(by=By.XPATH, value='/html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div/div[3]/div/div/div[2]/div[1]/span/a').get_attribute('href')
            geo_sc = data2.select(".w.MD._S")

            # NAME
            if name_sc:
                name.append(name_sc[0].text.lstrip())
            else:
                name.append('-')
            print(name)

            # REVIEW COUNT
            if reviews_sc:
                x = reviews_sc[0].text
                x = x.split()
                review_count.append(x[0])
            else:
                review_count.append('-')
            print(review_count)

            # ADDRESS
            if address_sc:
                address.append(address_sc.lstrip())
            else:
                address.append('-')
            print(address)

            # CONTACT
            if contact_sc:
                contact.append(contact_sc.lstrip())
            else:
                contact.append('-')
            print(contact)

            # EMAIL
            if email_sc:
                a = email_sc.find('a')
                if a.is_empty_element:
                    print('None')
                else:
                    email.append(a['href'])
            else:
                email.append('-')
            print(email)

            # WEBSITE
            if websiteurl_sc:
                website.append(websiteurl_sc.lstrip())
            else:
                website.append('-')
            print(website)

            # GEOCODES
            if geo_sc:
                geo = geo_sc[0]['src'].lstrip()
                codes = re.search(r'center=(.*?)&', geo).group(1)
                print(codes)
                geocodes.append(codes)
            else:
                geocodes.append('-')
            print(geocodes)

            WebDriverWait(driver2, 10)

            try:

                WebDriverWait(driver2, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='OTyAN _S b']"))).click()
            except:
                pass

            # Load the url
            url = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(url, 'lxml')
            WebDriverWait(driver2, 10)

            about_sc = data2.select(".jmnaM")
            features_sc = data2.findAll("div", {"class": "SrqKb"})

            if about_sc:
                description.append(about_sc[0].text.lstrip())
            else:
                description.append('-')
            print(description)












obj = TripAdvisorRestaurantScraper()
driver = obj.getdriver()
df = pd.read_csv("../datasets/cities.csv")

for index, row in df.iterrows():
    time.sleep(5)
    obj.search_for_restaurants(driver=driver, city=row['name_en'])
    time.sleep(10)
    data = obj.scrape_restaurant_data(driver=driver, city=row['name_en'])
    time.sleep(10)
    if data.empty is True:
        print("No Data")
    else:
        time.sleep(5)
        obj.scraping_restaurant_information(driver, data)
    driver.get("https://www.tripadvisor.com")
    if index == 6:
        break

# time.sleep(5)
# obj.search_for_restaurants(driver=driver, city="Kandy")
# time.sleep(10)
# obj.scrape_restaurant_data(driver=driver, city="Kandy")
# time.sleep(10)
# driver.get("https://www.tripadvisor.com")
driver.quit()
