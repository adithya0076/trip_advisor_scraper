import traceback

import bs4
import pandas as pd
import re
import random

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
        self.selenium_helper.check_connection()
        # Finds the Restaurant's page button
        status, things = self.selenium_helper.find_xpath_element(
            driver=driver, xpath="//a[@href='/Attractions']",
            is_get_text=False
        )
        things.click()
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
        self.selenium_helper.check_connection()
        status, ad = self.selenium_helper.find_xpath_element(
            driver=driver, xpath="//div[@class='UsGfI I']//button", is_get_text=False
        )

        try:
            ad.click()
        except:
            pass

        self.selenium_helper.sleep_time(5)

        status, see_all = self.selenium_helper.find_xpath_element(
            driver=driver, xpath="//div[@class='BYvbL A YeunF']//div[@class='Fofmq']/a",

        )

        try:
            web = see_all.get_attribute('href')
            driver.get(web)
        except:
            pass

        self.selenium_helper.sleep_time(random.randint(5, 10))

        # Gets the current source page
        source = driver.page_source

        # Use bs4 to parse data from the source
        data = bs4.BeautifulSoup(source, 'lxml')

        self.selenium_helper.sleep_time(random.randint(5, 10))

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
        self.selenium_helper.sleep_time(random.randint(5, 10))

        # This code while loop below loops through any pagination available
        a = 1
        while a:
            try:
                # scroll
                self.selenium_helper.driver_execute(
                    driver=driver, program="window.scrollTo(0, document.body.scrollHeight);"
                )

                self.selenium_helper.sleep_time(random.randint(5, 10))

                status, btnNext = self.selenium_helper.find_xpath_element(
                    driver=driver,
                    xpath="//div[@class='UCacc']//a[@data-smoke-attr='pagination-next-arrow']",
                    is_get_text=False
                )

                btnNext.click()
                # element.click()
                self.selenium_helper.sleep_time(random.randint(5, 10))

                # Gets the current SOURCE
                source = driver.page_source

                # Use bs4 to parse data from the URL
                data = bs4.BeautifulSoup(source, 'lxml')

                self.selenium_helper.sleep_time(random.randint(5, 10))

                # Selects the elements
                attractions = data.select(".VLKGO")

                for i in attractions:
                    a = i.find('a')
                    if a.is_empty_element:
                        print('None')
                    else:
                        link = 'https://www.tripadvisor.com/' + a['href'] + ''
                        urls.append(link)
            except:
                traceback.print_exc()
                break

        dict2 = {'city': city, 'url': urls, }
        fd = pd.DataFrame(dict2)
        return fd

    def scraping_attraction_information(self, driver, data):
        """
        Scrape the Details about each attraction from iterating through the links

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
            name_sc = data2.select('.biGQs._P.fiohW.eIegw')
            status, review_sc = self.selenium_helper.find_xpath_element(
                driver=driver, xpath="//span[@class='biGQs _P pZUbB biKBZ KxBGd']//span",
                is_get_text=True
            )
            status, address_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//button[@class='UikNM _G B- _S _T c G_ P0 wSSLS wnNQG raEkE']//span",
                is_get_text=True
            )
            status, email_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='WoBiw']//a[starts-with(@href,'mailto')]",
                is_get_text=False
            )
            status, contact_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='WoBiw']//a[starts-with(@href,'tel')]",
                is_get_text=False
            )
            status, website_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='WoBiw']//a[starts-with(@href,'http')]",
                is_get_text=False
            )
            status, description_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='IxAZL']//div[@class='biGQs _P pZUbB KxBGd']",
                is_get_text=True
            )
            status, geocodes_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//img[@class='oPZZx']",
                is_get_text=False
            )
            status, feature_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='biGQs _P pZUbB KxBGd']//div[@class='fIrGe _T bgMZj']",
                is_get_text=True
            )

            # get the city id
            condition = "city_name = '%s'" % row['city']
            city_id = self.db.select_record(table_name='city', condition=condition)
            _dict_info['city_id'] = city_id['id']
            self.selenium_helper.sleep_time(random.randint(5, 10))

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
            if review_sc:
                _dict_info['attraction_review_count'] = review_sc.lstrip()
            else:
                _dict_info['attraction_review_count'] = '-'

            # ADDRESS
            if address_sc:
                _dict_info['attraction_address'] = address_sc.lstrip()
            else:
                _dict_info['attraction_address'] = '-'

            # CONTACT
            if contact_sc:
                href = contact_sc.get_attribute('href').lstrip().split('%')
                href.pop(0)
                contact = '+'
                for i in href:
                    contact = str(contact) + str(i[2:])
                _dict_info['attraction_contact'] = contact
            else:
                _dict_info['attraction_contact'] = '-'

            # EMAIL
            if email_sc:
                _dict_info['attraction_email'] = email_sc.get_attribute('href').lstrip()
            else:
                _dict_info['attraction_email'] = '-'

            # WEBSITE
            if website_sc:
                _dict_info['attraction_website'] = website_sc.get_attribute('href').lstrip()
            else:
                _dict_info['attraction_website'] = '-'

            # GEOCODES
            if geocodes_sc:
                geo = geocodes_sc.get_attribute('src').lstrip()
                codes = re.search(r'center=(.*?)&', geo).group(1)
                geocodes.append(codes)
            else:
                geocodes.append('-,-')
            geo_c = geocodes[0].split(',')
            _dict_info['attraction_geocode_lan'] = geo_c[0]
            _dict_info['attraction_geocode_lon'] = geo_c[1]


            # DESCRIPTION
            if description_sc:
                _dict_info['attraction_description'] = description_sc.lstrip()
            else:
                _dict_info['attraction_description'] = '-'

            if feature_sc:
                feature = feature_sc.split(' • ')
                for i in feature:
                    feature_type.append(i)
                _dict_info['attraction_type'] = feature_type
            else:
                pass

            self.selenium_helper.sleep_time(random.randint(5, 10))

            # images
            status, img = self.selenium_helper.find_xpath_element(
                driver=driver, xpath="//button[@class='BrOJk u j z _F wSSLS HuPlH IyzRb']", is_get_text=False
            )
            try:
                img.click()
            except:
                pass
            self.selenium_helper.sleep_time(random.randint(5, 10))
            # Load the url
            source = driver.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(source, 'lxml')

            WebDriverWait(driver, 10)
            for items in data2.select(".cfCAA.w._Z.GA"):
                image = items['style'].split("url(")[1].split(")")[0]
                images.append(image)

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

