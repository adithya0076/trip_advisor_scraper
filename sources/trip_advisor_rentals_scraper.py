import traceback

import bs4
import pandas as pd
import re
import random

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait


class TripAdvisorRentalsScraper:

    def __init__(self, obj, db):
        self.selenium_helper = obj
        self.db = db

    def search_for_rentals(self, driver, city):
        """
        This function opens the Rental's page from the home screen and the search for the city.

        Args:
            driver (Geckodriver): The driver where the url is opened.
            city: The city to which to be searched.
        :param driver:
        :param city:
        :return:
        """
        self.selenium_helper.check_connection()
        # Finds the Restaurant's page button
        self.selenium_helper.click_xpath(driver=driver, xpath="//a[@href='/Rentals']")
        WebDriverWait(driver, 5)
        self.selenium_helper.sleep_time(random.randint(5, 8))
        # Finds the input
        status, search = self.selenium_helper.find_xpath_element(
            driver=driver,
            xpath="//div[@class='kaEuY']//input[@placeholder='Where to?']",
            is_get_text=False
        )
        search.send_keys(city)
        WebDriverWait(driver, 10)
        self.selenium_helper.sleep_time(random.randint(5, 10))
        search.send_keys(Keys.ENTER)
        print(f"The city: '{city}' is searched")

    def traverse_through_cities(self, driver):
        """
        Gets the urls of the first page.
        Args:
            driver:
            city:

        Returns:

        """
        self.selenium_helper.check_connection()
        url_list = []
        # Gets the current URLf
        source = driver.page_source
        print(f"URL is loaded")

        # Use bs4 to parse data from the URL
        data = bs4.BeautifulSoup(source, 'lxml')
        current_url = driver.current_url
        cities = data.select('.QJCkX')

        # Saving the urls of Restaurants available
        for i in cities:
            a = i.find('a')
            if a.is_empty_element:
                print('None')
            else:
                link = 'https://www.tripadvisor.com/' + a['href'] + ''
                url_list.append(link)

        print(url_list)

        for i in url_list:
            driver.get(i)
            self.scrape_rental_data(driver=driver)

    def scrape_rental_data(self, driver):
        """
        This function is using bs4 to scrape current page source for Rentals.

        Args:
            driver (Geckodriver): The driver where the url is opened.

        Returns:
            The pandas dataframe which the scraped data are saved into.
        :param driver:
        :return df:
        """
        self.selenium_helper.check_connection()
        # Gets the current URL
        source = driver.page_source
        print(f"URL is loaded")

        # Use bs4 to parse data from the URL
        data = bs4.BeautifulSoup(source, 'lxml')

        # Selects the elements
        rentals = data.select(".zxMUq.f")

        urls = []

        # Saving the urls of Restaurants available
        for i in rentals:
            a = i.find('a')
            if a.is_empty_element:
                print('None')
            else:
                link = 'https://www.tripadvisor.com/' + a['href'] + ''
                urls.append(link)

        # Checking whether next button is available
        wait = WebDriverWait(driver, 10)
        self.selenium_helper.sleep_time(random.randint(5, 10))

        a = 1
        while a:
            print("Clicked")
            try:
                self.selenium_helper.sleep_time(random.randint(5, 10))
                self.selenium_helper.driver_execute(driver=driver, program="window.scrollTo(0, document.body.scrollHeight);")
                self.selenium_helper.click_xpath(driver=driver, xpath="//button[@aria-label='Close' and @type='button']")
                btnNext = self.selenium_helper.click_xpath(driver=driver, xpath="//span[@class='ui_button nav next primary ']")
                if btnNext is False:
                    break
                else:
                    pass
                self.selenium_helper.sleep_time(random.randint(5, 10))

                # Gets the current URL
                source = driver.page_source
                print(f"URL is loaded")

                # Use bs4 to parse data from the URL
                data = bs4.BeautifulSoup(source, 'lxml')

                # Selects the elements
                rentals = data.select(".zxMUq.f")

                self.selenium_helper.sleep_time(random.randint(5, 10))

                for i in rentals:
                    a = i.find('a')
                    if a.is_empty_element:
                        print('None')
                    else:
                        link = 'https://www.tripadvisor.com/' + a['href'] + ''
                        urls.append(link)
                dict2 = {'type_id': 4, 'url': urls, }
                fd = pd.DataFrame(dict2)
                self.db.base_job_handler(fd)
            except Exception as e:
                print(e)

    def scraping_rental_information(self, driver, data):
        """
        Scrape the Details about each rental from iterating through the links

        :param driver:
        :param data:
        :return:
        """
        self.selenium_helper.check_connection()
        for index, row in data.iterrows():
            _dict_info = {}
            geocodes = []
            images = []
            feature_type = []

            driver.get(row['url'])
            self.selenium_helper.sleep_time(random.randint(5, 10))

            # Load the url
            source = driver.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(source, 'lxml')
            WebDriverWait(driver, 10)

            # Elements which are selected
            name_sc = data2.select('.IaFsP.propertyHeading')
            status, review_sc = self.selenium_helper.find_xpath_element(
                driver=driver, xpath="//div[@class='jjmLo _S']//span[@class='NM Wb']",
                is_get_text=True
            )
            status, description_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='fhxGl H4']",
                is_get_text=True
            )
            status, price_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//span[@class='RFDoO b']",
                is_get_text=True
            )
            status, bedrooms_sc = self.selenium_helper.find_xpath_elements(
                driver=driver,
                xpath="//div[@class='VPOMc']",
                is_get_text=True
            )
            status, rentaltype_sc = self.selenium_helper.find_xpath_elements(
                driver=driver,
                xpath="//div[@class='gjgYb b']",
                is_get_text=True
            )
            status, geocodes_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='RHUrB']//a[starts-with(@href,'https://maps.google.com')]",
                is_get_text=False
            )
            status, feature_sc = self.selenium_helper.find_xpath_elements(
                driver=driver,
                xpath="//div[@class='jlCLL']",
                is_get_text=True
            )
            status, owner_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='fwnAY b']",
                is_get_text=True
            )
            status, city_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//ul[@class='breadcrumbs']/li[last()]//span",
                is_get_text=True
            )
            if city_sc:
                pass
                # get the city id
                condition = "city_name = '%s'" % city_sc.lstrip()
                city_id = self.db.select_record(table_name='city', condition=condition)
                if city_id:
                    _dict_info['city_id'] = city_id['id']
                else:
                    city = self.db.insert_city(table_name='city',
                                               city=re.search(r'(?<=in ).*', city_sc.lstrip()).group())
                    _dict_info['city_id'] = city['id']
            else:
                status, city_sc = self.selenium_helper.find_xpath_element(
                    driver=driver,
                    xpath="//div[@class='VGRgp']/span[2]",
                    is_get_text=True
                )
                city = city_sc.split(',')
                # get the city id

                condition = "city_name = '%s'" % city[0]
                city_id = self.db.select_record(table_name='city', condition=condition)
                if city_id:
                    _dict_info['city_id'] = city_id['id']
                else:
                    city_i = self.db.insert_city(table_name='city', city=city[0])
                    _dict_info['city_id'] = city_i['id']

            self.selenium_helper.sleep_time(random.randint(5, 10))

            # NAME
            if name_sc:
                try:
                    name = re.search(r'(\d+[.] )', name_sc[0].text.lstrip()).group(1)
                    _dict_info['name'] = name_sc[0].text.lstrip().replace(name, '').lstrip()
                except:
                    _dict_info['name'] = name_sc[0].text.lstrip()
            else:
                _dict_info['name'] = ''

            # REVIEW COUNT
            if review_sc:
                _dict_info['rental_review_count'] = review_sc.lstrip()
            else:
                _dict_info['rental_review_count'] = ''

            # GEOCODES
            if geocodes_sc:
                geo = geocodes_sc.get_attribute('href').lstrip()
                codes = re.search(r'll=(.*?)&', geo).group(1)
                geocodes.append(codes)
            else:
                geocodes.append('-,-')
            geo_c = geocodes[0].split(',')
            _dict_info['rental_geocode_lan'] = geo_c[0]
            _dict_info['rental_geocode_lon'] = geo_c[1]

            # DESCRIPTION
            if description_sc:
                _dict_info['rental_description'] = description_sc.lstrip()
            else:
                _dict_info['rental_description'] = ''

            # PRICE
            if price_sc:
                _dict_info['rental_price'] = price_sc.lstrip()
            else:
                _dict_info['rental_price'] = ''

            # BEDROOMS
            if bedrooms_sc:
                _dict_info['rental_bedrooms'] = bedrooms_sc[0].lstrip()
                _dict_info['rental_bathrooms'] = bedrooms_sc[1].lstrip()
                _dict_info['rental_guests'] = bedrooms_sc[2].lstrip()
                _dict_info['rental_night_min'] = bedrooms_sc[3].lstrip()
            else:
                _dict_info['rental_bedrooms'] = ''
                _dict_info['rental_bathrooms'] = ''
                _dict_info['rental_guests'] = ''
                _dict_info['rental_nights_min'] = ''

            # RENTAL TYPE
            if rentaltype_sc:
                _dict_info['rental_type'] = rentaltype_sc.lstrip()
            else:
                _dict_info['rental_type'] = ''

            # RENTAL TYPE
            if owner_sc:
                _dict_info['rental_owner'] = owner_sc.lstrip()
            else:
                _dict_info['rental_owner'] = ''

            # FEATURES
            if feature_sc:
                for i in feature_sc:
                    feature_type.append(i.lstrip())
                _dict_info['rental_feature'] = feature_type
            else:
                pass

            self.selenium_helper.sleep_time(random.randint(5, 10))

            # images
            status, ad = self.selenium_helper.find_xpath_element(
                driver=driver, xpath="//div[@class='UsGfI I']//button", is_get_text=False
            )

            try:
                ad.click()
            except:
                print("No ad")

            img = self.selenium_helper.click_xpath(driver=driver, xpath="//span[@class='nJpAk S5 _S']")
            self.selenium_helper.sleep_time(random.randint(5, 10))
            status, img_sc = self.selenium_helper.find_xpath_elements(driver=driver, xpath="//div[@class='hSWDD']//img", is_get_text=False)
            self.selenium_helper.sleep_time(random.randint(5, 10))

            # Load the url
            source = driver.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(source, 'lxml')

            WebDriverWait(driver, 10)
            if img_sc:
                for i in img_sc:
                    images.append(i.get_attribute('src').lstrip())
            else:
                pass

            _dict_info['url'] = row['url']

            if images:
                _dict_info['image'] = images
            else:
                pass

            self.selenium_helper.sleep_time(random.randint(5, 10))

            print(_dict_info)

            df = pd.DataFrame([_dict_info])
            # save to db
            self.db.base_job_handler(df)

            self.selenium_helper.sleep_time(random.randint(5, 10))