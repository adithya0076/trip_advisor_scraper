import bs4
import pandas as pd
import re
import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TripAdvisorRestaurantScraper:

    def __init__(self, obj, db):
        self.SCRAPING_URL = "https://www.tripadvisor.com"
        self.selenium_helper = obj
        self.db = db

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
        self.selenium_helper.sleep(10)
        # Finds the input
        search = driver.find_element(by=By.XPATH, value="//div[@class='kaEuY']//input[@placeholder='Where to?']")

        search.send_keys(city)
        WebDriverWait(driver, 10)
        self.selenium_helper.sleep(random.randint(5, 10))
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
        source = driver.page_source
        print(f"URL is loaded")

        # Use bs4 to parse data from the URL
        data = bs4.BeautifulSoup(source, 'lxml')

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
        self.selenium_helper.sleep(15)

        a = 1
        while a:
            print("Clicked")
            try:
                # element = wait.until(EC.element_to_be_clickable(
                #     (By.XPATH, "//a[@class='ui_button next primary']")))
                # print("clickable")
                self.selenium_helper.sleep(10)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # self.selenium_helper.sleep(6)
                try:

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[@aria-label='Close' and @type='button']"))).click()
                except:
                    pass
                driver.find_element(by=By.XPATH, value="//a[@class='nav next rndBtn ui_button primary taLnk']").click()
                # element.click()
                self.selenium_helper.sleep(10)

                # Gets the current URL
                source = driver.page_source
                print(f"URL is loaded")

                # Use bs4 to parse data from the URL
                data = bs4.BeautifulSoup(source, 'lxml')

                # Selects the elements
                restaurants = data.select(".RfBGI")

                self.selenium_helper.sleep(5)

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

        for index, row in data.iterrows():
            _dict_info = {}
            geocodes = []
            features = []
            images = []

            driver2.get(row['url'])
            self.selenium_helper.sleep(10)

            # Load the url
            source = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(source, 'lxml')
            WebDriverWait(driver2, 10)

            # Elements which are selected
            name_sc = data2.select(".HjBfq")
            reviews_sc = data2.select(".AfQtZ")
            status, address_sc = self.selenium_helper.find_xpath_element(driver=driver2,
                                                                         xpath="/html/body/div[2]/div[1]/div/div[4]/div/div/div[3]/span[1]/span/a",
                                                                         is_get_text=True)

            status, contact_sc = self.selenium_helper.find_xpath_element(driver=driver2,
                                                                         xpath="/html/body/div[2]/div[1]/div/div[4]/div/div/div[3]/span[2]/span/span[2]/a",
                                                                         is_get_text=True)

            try:
                features_sc = data2.findAll("div", {"class": "SrqKb"})
            except:
                pass

            email_sc = None
            websiteurl_sc = None
            geo_sc = None
            try:
                email_sc = data2.select(".IdiaP.Me.sNsFa")

                websiteurl_sc = driver2.find_element(by=By.XPATH,
                                                     value="//a[@class='YnKZo Ci Wc _S C AYHFM']").get_attribute('href')
                geo_sc = data2.select(".w.MD._S")
            except:
                pass

            # get the city id
            condition = "city_name = '%s'" % row['city']
            city_id = self.db.select_record(table_name='city', condition=condition)
            _dict_info['city_id'] = city_id['id']
            self.selenium_helper.sleep(5)

            # NAME
            if name_sc:
                try:
                    name = re.search(r'(\d+[.] )', name_sc[0].text.lstrip()).group(1)
                    _dict_info['name'] = name_sc[0].text.lstrip().replace(name, '').lstrip()
                except:
                    _dict_info['name'] = name_sc[0].text.lstrip()
            else:
                _dict_info['name'] = '-'

            # REVIEW COUNT
            if reviews_sc:
                x = reviews_sc[0].text.split()
                _dict_info['restaurant_review_count'] = reviews_sc[0].text.split()[0]
            else:
                _dict_info['restaurant_review_count'] = '-'

            # ADDRESS
            if address_sc:
                _dict_info['restaurant_address'] = address_sc.lstrip()
            else:
                _dict_info['restaurant_address'] = '-'

            # CONTACT
            if contact_sc:
                _dict_info['restaurant_contact'] = contact_sc.lstrip()
            else:
                _dict_info['restaurant_contact'] = '-'
            print(contact_sc.lstrip())
            # EMAIL
            for em in email_sc:
                a = em.find('a')
                if a:
                    _dict_info['restaurant_email'] = a['href']
                else:
                    _dict_info['restaurant_email'] = '_'

            # WEBSITE
            if websiteurl_sc:
                _dict_info['restaurant_website'] = websiteurl_sc.lstrip()
            else:
                _dict_info['restaurant_website'] = '-'

            # GEOCODES
            if geo_sc:
                geo = geo_sc[0]['src'].lstrip()
                codes = re.search(r'center=(.*?)&', geo).group(1)
                print(codes)
                geocodes.append(codes)
            else:
                geocodes.append('-,-')
            print(geocodes)
            geo_c = geocodes[0].split(',')
            _dict_info['restaurant_geocode_lan'] = geo_c[0]
            _dict_info['restaurant_geocode_lon'] = geo_c[1]

            for i in features_sc:
                x = i.text
                currency = x[:3]
                if currency == "LKR":
                    pass
                else:
                    features.append(x)

            WebDriverWait(driver2, 10)

            try:

                WebDriverWait(driver2, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@class='OTyAN _S b']"))).click()
            except:
                pass

            # Load the url
            source = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(source, 'lxml')
            WebDriverWait(driver2, 10)
            try:
                about_sc = data2.select(".jmnaM")

                status, price_sc = self.selenium_helper.find_xpath_element(
                    driver=driver2,
                    xpath='//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/div[14]/div/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div[2]',
                    is_get_text=True
                )
            except:
                pass

            if about_sc:
                _dict_info['restaurant_description'] = about_sc[0].text.lstrip()
            else:
                _dict_info['restaurant_description'] = '-'

            if price_sc:
                currency = price_sc[:3]
                if currency == "LKR":
                    _dict_info['restaurant_price_range'] = price_sc.lstrip()
                else:
                    _dict_info['restaurant_price_range'] = '-'
            else:
                _dict_info['restaurant_price_range'] = '-'

            # getting the images
            self.selenium_helper.sleep(5)
            driver2.find_element(By.XPATH, "//div[@class='zPIck _Q Z1 t _U c _S zXWgK']").click()
            self.selenium_helper.sleep(5)
            try:

                driver2.find_element(By.XPATH,
                                     "/html/body/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/span/span[2]").click()
            except:
                pass
            self.selenium_helper.sleep(5)
            # Load the url
            source = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(source, 'lxml')
            try:
                WebDriverWait(driver2, 10)
                self.selenium_helper.sleep(5)
                dialog = driver2.find_element(by=By.XPATH, value="//div[@class='photoGridWrapper']")
                self.selenium_helper.sleep(5)
                sc = driver2.execute_script("return document.querySelector('.photoGridWrapper').scrollHeight")
                while True:
                    driver2.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)

                    self.selenium_helper.sleep(2)
                    dialog = driver2.find_element(by=By.XPATH, value="//div[@class='photoGridWrapper']")
                    sc_2 = driver2.execute_script("return document.querySelector('.photoGridWrapper').scrollHeight")

                    if sc_2 == sc:
                        break
                    sc = sc_2

                WebDriverWait(driver2, 5)
                self.selenium_helper.sleep(5)
                image_sc = data2.select('.fillSquare')
                for i in image_sc:
                    img = i.find('img')
                    if img.has_attr('src'):
                        images.append(img['src'])
                    else:
                        pass
            except:
                pass

            print(images)

            _dict_info['url'] = row['url']

            if images:
                _dict_info['image'] = images
            else:
                pass

            if features:
                _dict_info['feature_type'] = features
            else:
                pass

            self.selenium_helper.sleep(5)

            print(_dict_info)

            df = pd.DataFrame([_dict_info])
            # save to db
            self.db.base_job_handler(df)

            self.selenium_helper.sleep(5)
