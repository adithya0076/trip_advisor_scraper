import bs4
import pandas as pd
import re
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TripAdvisorRestaurantScraper:

    def __init__(self, obj, db):
        self.selenium_helper = obj
        self.db = db

    def search_for_restaurants(self, driver, city):
        self.selenium_helper.check_connection()
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
        status, restaurant = self.selenium_helper.find_xpath_element(driver=driver, xpath="//a[@href='/Restaurants']",
                                                                     is_get_text=False)
        restaurant.click()
        WebDriverWait(driver, 10)
        self.selenium_helper.sleep_time(10)
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
        cities = data.select('.geo_image')

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
            self.scrape_restaurant_data(driver=driver)

        return current_url

    def traverse_through_cities_pagination(self, driver, current_url):
        self.selenium_helper.check_connection()
        driver.get(current_url)
        url_list = []
        a = 1
        self.selenium_helper.sleep_time(random.randint(1, 5))
        self.selenium_helper.driver_execute(driver=driver, program="window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Close' and @type='button']"))).click()
        except:
            pass
        self.selenium_helper.click_xpath(driver=driver,
                                         xpath="//a[@class='nav next rndBtn ui_button primary taLnk']")
        while a:
            try:
                self.selenium_helper.sleep_time(random.randint(5, 10))

                # Gets the current URL
                source = driver.page_source
                print(f"URL is loaded")

                # Use bs4 to parse data from the URL
                data = bs4.BeautifulSoup(source, 'lxml')

                status, li_sc = self.selenium_helper.find_xpath_elements(driver=driver,
                                                                         xpath="//ul[@class='geoList']//li[*]//a",
                                                                         is_get_text=False)

                # Saving the urls of Restaurants available
                for i in li_sc:
                    if i:
                        link = i.get_attribute('href').lstrip() + ''
                        url_list.append(link)
                    else:
                        print('None')

                btnNext = self.selenium_helper.click_xpath(driver=driver,
                                                           xpath="//a[@class='guiArw sprite-pageNext ']")

                if btnNext is False:
                    break
                else:
                    pass
            except Exception as e:
                print(e)

        for i in url_list:
            driver.get(i)
            self.scrape_restaurant_data(driver)

    def scrape_restaurant_data(self, driver):
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
        self.selenium_helper.sleep_time(random.randint(5, 10))

        a = 1
        while a:
            print("Clicked")
            try:
                # element = wait.until(EC.element_to_be_clickable(
                #     (By.XPATH, "//a[@class='ui_button next primary']")))
                # print("clickable")
                self.selenium_helper.sleep_time(random.randint(5, 10))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # self.selenium_helper.sleep_time(6)
                try:

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[@aria-label='Close' and @type='button']"))).click()
                except:
                    pass
                status, btnNext = self.selenium_helper.find_xpath_element(
                    driver=driver, xpath="//a[@class='nav next rndBtn ui_button primary taLnk']", is_get_text=False
                )
                btnNext.click()
                # element.click()
                self.selenium_helper.sleep_time(random.randint(5, 10))

                # Gets the current URL
                source = driver.page_source
                print(f"URL is loaded")

                # Use bs4 to parse data from the URL
                data = bs4.BeautifulSoup(source, 'lxml')

                # Selects the elements
                restaurants = data.select(".RfBGI")

                self.selenium_helper.sleep_time(random.randint(5, 10))

                for i in restaurants:
                    a = i.find('a')
                    if a.is_empty_element:
                        print('None')
                    else:
                        link = 'https://www.tripadvisor.com/' + a['href'] + ''
                        urls.append(link)
                dict2 = {'type_id': 1, 'url': urls, }
                fd = pd.DataFrame(dict2)
                self.db.base_job_handler(fd)
            except Exception as e:
                print(e)
                break

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
            self.selenium_helper.sleep_time(10)

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
            status, city_sc = self.selenium_helper.find_xpath_element(
                driver=driver,
                xpath="//span[@class='DsyBj cNFrA']//a//span[contains(text(), 'in')]",
                is_get_text=True
            )

            if city_sc:
                pass
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

            try:
                features_sc = data2.findAll("div", {"class": "SrqKb"})
            except:
                pass

            email_sc = None
            websiteurl_sc = None
            geo_sc = None
            try:
                email_sc = data2.select(".IdiaP.Me.sNsFa")
                status, web = self.selenium_helper.find_xpath_element(
                    driver=driver2, xpath="//a[@class='YnKZo Ci Wc _S C AYHFM']", is_get_text=False
                )
                websiteurl_sc = web.get_attribute('href')
                geo_sc = data2.select(".w.MD._S")
            except:
                pass

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
            if reviews_sc:
                x = reviews_sc[0].text.split()
                _dict_info['restaurant_review_count'] = reviews_sc[0].text.split()[0]
            else:
                _dict_info['restaurant_review_count'] = ''

            # ADDRESS
            if address_sc:
                _dict_info['restaurant_address'] = address_sc.lstrip()
            else:
                _dict_info['restaurant_address'] = ''

            # CONTACT
            if contact_sc:
                _dict_info['restaurant_contact'] = contact_sc.lstrip()
            else:
                _dict_info['restaurant_contact'] = ''
            print(contact_sc.lstrip())
            # EMAIL
            for em in email_sc:
                a = em.find('a')
                if a:
                    _dict_info['restaurant_email'] = a['href']
                else:
                    _dict_info['restaurant_email'] = ''

            # WEBSITE
            if websiteurl_sc:
                _dict_info['restaurant_website'] = websiteurl_sc.lstrip()
            else:
                _dict_info['restaurant_website'] = ''

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
                    cat = x.split(',')
                    for item in cat:
                        features.append(item.lstrip())

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
                _dict_info['restaurant_description'] = ''

            if price_sc:
                currency = price_sc[:3]
                if currency == "LKR":
                    _dict_info['restaurant_price_range'] = price_sc.lstrip()
                else:
                    _dict_info['restaurant_price_range'] = ''
            else:
                _dict_info['restaurant_price_range'] = ''

            # getting the images
            self.selenium_helper.sleep_time(random.randint(5, 10))

            self.selenium_helper.click_xpath(driver=driver, xpath="//div[@class='see_all_count_wrap']//span//span[@class='details']")
            self.selenium_helper.sleep_time(5)
            try:
                status, btnImg = self.selenium_helper.find_xpath_element(
                    driver=driver2,
                    xpath="/html/body/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/span/span[2]",
                    is_get_text=False
                )
                btnImg.click()
            except:
                pass
            self.selenium_helper.sleep_time(5)
            # Load the url
            source = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(source, 'lxml')
            try:
                WebDriverWait(driver2, 10)
                self.selenium_helper.sleep_time(5)
                status, dialog = self.selenium_helper.find_xpath_element(
                    driver=driver2, xpath="//div[@class='photoGridWrapper']", is_get_text=False
                )
                self.selenium_helper.sleep_time(5)
                sc = driver2.execute_script("return document.querySelector('.photoGridWrapper').scrollHeight")
                while True:
                    driver2.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)

                    self.selenium_helper.sleep_time(2)
                    status, dialog = self.selenium_helper.find_xpath_element(
                        driver=driver2, xpath="//div[@class='photoGridWrapper']", is_get_text=False
                    )
                    sc_2 = driver2.execute_script("return document.querySelector('.photoGridWrapper').scrollHeight")

                    if sc_2 == sc:
                        break
                    sc = sc_2

                WebDriverWait(driver2, 5)
                self.selenium_helper.sleep_time(5)
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

            print(features)

            self.selenium_helper.sleep_time(random.randint(5, 10))

            print(_dict_info)

            df = pd.DataFrame([_dict_info])
            # save to db
            self.db.base_job_handler(df)

            self.selenium_helper.sleep_time(random.randint(5, 10))
