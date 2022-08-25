import traceback

import bs4
import pandas as pd
import re
import random

from pyasn1.compat.octets import null
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TripAdvisorHotelsScraper:

    def __init__(self, obj, db):
        self.selenium_helper = obj
        self.db = db

    def search_for_hotels(self, driver, city):
        """
        This function opens the hotel's page from the home screen and the search for the city.

        Args:
            driver (Geckodriver): The driver where the url is opened.
            city: The city to which to be searched.
        :param driver:
        :param city:
        :return:
        """
        self.selenium_helper.check_connection()
        # Finds the Restaurant's page button
        status, hotels = self.selenium_helper.find_xpath_element(
            driver=driver, xpath="//a[@href='/Hotels']",
            is_get_text=False
        )
        hotels.click()
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

    def scrape_hotel_data(self, driver, city):
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
            driver=driver, xpath="//button[@class='rmyCe _G B- z _S c Wc wSSLS pexOo sOtnj']",

        )

        try:
            see_all.click()
        except:
            pass

        self.selenium_helper.sleep_time(random.randint(5, 10))

        # Gets the current source page
        source = driver.page_source

        # Use bs4 to parse data from the source
        data = bs4.BeautifulSoup(source, 'lxml')

        self.selenium_helper.sleep_time(random.randint(5, 10))

        # Selects the elements
        attractions = data.select(".listing_title")

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
                    xpath="//span[text()='Next']",
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
                attractions = data.select(".listing_title")

                for i in attractions:
                    a = i.find('a')
                    if a.is_empty_element:
                        print('None')
                    else:
                        link = 'https://www.tripadvisor.com/' + a['href'] + ''
                        urls.append(link)

                dict2 = {'type_id': 2, 'url': urls, }
                fd = pd.DataFrame(dict2)
                self.db.base_job_handler(fd)
            except:
                traceback.print_exc()
                break

    def scraping_hotel_information(self, driver, data):
        """
        Scrape the Details about each hotel from iterating through the links

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

            # Elements which are selected
            name_sc = data2.select('.QdLfr.b.d.Pn')
            status, review_sc = self.selenium_helper.find_xpath_element(
                driver=driver, xpath="//span[@class='qqniT']",
                is_get_text=True
            )
            status, price_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='WXMFC b']",
                is_get_text=True
            )
            if price_sc:
                pass
            else:
                status, price_sc = self.selenium_helper.find_xpath_element(
                    driver=driver,
                    xpath="//div[@class='JPNOn b Wi']",
                    is_get_text=True
                )
            status, address_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='rrPHl hirPY']//span[@class='fHvkI PTrfg']",
                is_get_text=True
            )
            status, contact_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='eeVey S4 H3 f u LGJIs']//a[starts-with(@href,'tel')]",
                is_get_text=False
            )
            website_sc = data2.select(".YnKZo.Ci.Wc._S.C.pInXB._S.ITocq.jNmfd")
            description_sc = data2.select("._T.FKffI.IGtbc.Ci")
            class_sc = data2.select(".JXZuC.d.H0")
            status, geocodes_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//img[@class='klpje']",
                is_get_text=False
            )
            feature_sc = data2.select(".yplav.f.ME.H3._c")
            status, city_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//div[@class='cGAqf']//a//span",
                is_get_text=True
            )
            if city_sc:

                # get the city id
                condition = "city_name = '%s'" % re.search(r'(?<=in ).*', city_sc.lstrip()).group()
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

            self.selenium_helper.sleep_time(random.randint(1, 5))

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
                _dict_info['hotel_review_count'] = review_sc.split()[0]
            else:
                _dict_info['hotel_review_count'] = ''

            # PRICE
            if price_sc:
                _dict_info['hotel_price'] = price_sc.split()[1]
            else:
                _dict_info['hotel_price'] = ''

            # ADDRESS
            if address_sc:
                _dict_info['hotel_address'] = address_sc.lstrip()
            else:
                _dict_info['hotel_address'] = ''

            # CONTACT
            if contact_sc:
                href = contact_sc.get_attribute('href').lstrip().split(':')
                _dict_info['hotel_contact'] = href[1]
            else:
                _dict_info['hotel_contact'] = ''

            # CLASS
            if class_sc:
                star_count = class_sc[0]['aria-label'].split()
                _dict_info['hotel_class'] = star_count[0].lstrip()
            else:
                _dict_info['hotel_class'] = ''

            # WEBSITE
            if website_sc:
                _dict_info['hotel_website'] = 'https://www.tripadvisor.com/' + website_sc[0]['href']
            else:
                _dict_info['hotel_website'] = ''

            # GEOCODES
            if geocodes_sc:
                geo = geocodes_sc.get_attribute('src').lstrip()
                codes = re.search(r'center=(.*?)&', geo).group(1)
                geocodes.append(codes)
            else:
                geocodes.append('-,-')
            geo_c = geocodes[0].split(',')
            _dict_info['hotel_geocode_lan'] = geo_c[0]
            _dict_info['hotel_geocode_lon'] = geo_c[1]

            # DESCRIPTION
            if description_sc:
                _dict_info['hotel_description'] = description_sc[0].text.lstrip()
            else:
                _dict_info['hotel_description'] = ''

            # FEATURES
            if feature_sc:
                for i in feature_sc:
                    feature_type.append(i.getText().lstrip())
                _dict_info['hotel_type'] = feature_type
            else:
                pass

            # SOURCE
            _dict_info['url'] = row['url']

            status, ad = self.selenium_helper.find_xpath_element(
                driver=driver, xpath="//div[@class='UsGfI I']//button", is_get_text=False
            )

            try:
                ad.click()
            except:
                print("No ad")
            self.selenium_helper.sleep_time(random.randint(1, 5))

            try:
                self.selenium_helper.click_xpath(driver=driver, xpath="//span[@class='is-shown-at-tablet krMEp b']")
                self.selenium_helper.sleep_time(random.randint(1, 5))
                WebDriverWait(driver, 5)
                # images
                status, dialog = self.selenium_helper.find_xpath_element(driver=driver,
                                                                         xpath="//div[@class='SPERR _R z']",
                                                                         is_get_text=False)
                self.selenium_helper.click_xpath(driver=driver,
                                                 xpath="//button[@class='OKHdJ z Pc PQ Pp PD W _S Gn Z B2 BF _M PQFNM wSSLS']")
                self.selenium_helper.click_xpath(driver=driver,
                                                 xpath="//span[@class='whtrm _G z u Pi PW Pv PI _S Wh Wc B- Dtjvh'] ")

                # Scroll down
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight/2", dialog)

                self.selenium_helper.sleep_time(random.randint(1, 5))
                WebDriverWait(driver, 5)

                # Load the url
                url1 = driver.page_source

                # Use bs4 to parse data from the URL
                data3 = bs4.BeautifulSoup(url1, 'lxml')

                for items in data3.select(".cfCAA.w._Z.GA"):
                    image = items['style'].split("url(")[1].split(")")[0]
                    images.append(image)

                print('images', images)
                WebDriverWait(driver, 5)
                self.selenium_helper.sleep_time(random.randint(1, 5))

            except:
                self.selenium_helper.click_xpath(driver=driver,
                                                 xpath="//button[@class='RFOih _Z _S Q z Wc Wh _J gUFiK vuowK']")

                try:
                    self.selenium_helper.click_xpath(driver=driver,
                                                     xpath="//span[@class='is-shown-at-tablet krMEp b']")
                    self.selenium_helper.sleep_time(random.randint(1, 5))
                    WebDriverWait(driver, 5)

                    # images
                    status, dialog = self.selenium_helper.find_xpath_element(driver=driver,
                                                                             xpath="//div[@class='SPERR _R z']",
                                                                             is_get_text=False)
                    self.selenium_helper.click_xpath(driver=driver,
                                                     xpath="//button[@class='OKHdJ z Pc PQ Pp PD W _S Gn Z B2 BF _M PQFNM wSSLS']")

                    self.selenium_helper.click_xpath(driver=driver,
                                                     xpath="//span[@class='whtrm _G z u Pi PW Pv PI _S Wh Wc B- Dtjvh']")
                    # Scroll down
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight/2", dialog)

                    self.selenium_helper.sleep_time(random.randint(5, 10))
                    WebDriverWait(driver, 5)

                    # Load the url
                    url1 = driver.page_source

                    # Use bs4 to parse data from the URL
                    data3 = bs4.BeautifulSoup(url1, 'lxml')
                    self.selenium_helper.sleep_time(random.randint(5, 10))
                    for items in data3.select(".cfCAA.w._Z.GA"):
                        image = items['style'].split("url(")[1].split(")")[0]
                        images.append(image)

                    print('images', images)
                    WebDriverWait(driver, 5)
                except:
                    traceback.print_exc()

            if images:
                _dict_info['image'] = images
            else:
                pass

            print(_dict_info)

            df = pd.DataFrame([_dict_info])
            # save to db
            self.db.base_job_handler(df)
