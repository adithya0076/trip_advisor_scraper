import bs4
import pandas as pd
import re
import time
import random
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from helpers.selenium_helper import SeleniumHelper

from dbModel.BaseDb import BaseDB

# Database Connection
db = BaseDB()
con = db.con()


class TripAdvisorRestaurantScraper:

    def __init__(self):
        self.GECKO_DRIVER_PATH = "../driver/geckodriver"
        self.SCRAPING_URL = "https://www.tripadvisor.com"

        # Creating the service object to pass the executable geckodriver path to webdriver
        self.service_obj = Service(executable_path=self.GECKO_DRIVER_PATH)
        # self.profile_path = r'C:\Users\sinxdell\AppData\Roaming\Mozilla\Firefox\Profiles\2lfh6wg7.default-release'

        # Creating the Firefox options to add the additional options to the webdriver
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('ignore-ssl-errors')
        # self.options.set_preference('profile', self.profile_path)
        self.profile = FirefoxProfile()
        self.selenium_helper = SeleniumHelper()

    def getdriver(self):
        """
         Creating and returning the selenium webdriver.

         Uses firefox and the geckodriver.


        Returns:
         Geckodriver object: This driver object is used to simulate the firefox browser.
        :return driver_object:
        """

        driver = Firefox(options=self.options, firefox_profile=self.profile, service=self.service_obj)
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
        search = driver.find_element(by=By.XPATH, value="//div[@class='kaEuY']//input[@placeholder='Where to?']")

        search.send_keys(city)
        WebDriverWait(driver, 10)
        time.sleep(random.randint(5, 10))
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

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[@aria-label='Close' and @type='button']"))).click()
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

        for index, row in data.iterrows():
            _dict_info = {}
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
            address_sc = driver2.find_element(by=By.XPATH,
                                              value="/html/body/div[2]/div[1]/div/div[4]/div/div/div[3]/span[1]/span/a").text
            contact_sc = driver2.find_element(by=By.XPATH,
                                              value="/html/body/div[2]/div[1]/div/div[4]/div/div/div[3]/span[2]/span/span[2]/a").text

            # status, contact_sc = self.selenium_helper.find_xpath_element(driver=driver2, xpath="", is_get_text=True)

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

            # NAME
            if name_sc:
                _dict_info['name'] = name_sc[0].text.lstrip()
                name.append(name_sc[0].text.lstrip())
            else:
                _dict_info['name'] = ''
                name.append('-')
            print(name)

            # REVIEW COUNT
            if reviews_sc:
                x = reviews_sc[0].text.split()
                _dict_info['restaurant_review_count'] = reviews_sc[0].text.split()[0]
                # x = x.split()
                review_count.append(x[0])
            else:
                review_count.append('-')
                _dict_info['restaurant_review_count'] = '-'
            print(review_count)

            # ADDRESS
            if address_sc:
                address.append(address_sc.lstrip())
                _dict_info['restaurant_address'] = address_sc.lstrip()
            else:
                address.append('-')
                _dict_info['restaurant_address'] = '-'
            print(address)

            # CONTACT
            if contact_sc:
                contact.append(contact_sc.lstrip())
                _dict_info['restaurant_contact'] = contact_sc.lstrip()
            else:
                contact.append('-')
                _dict_info['restaurant_contact'] = '-'
            print(contact)

            # EMAIL
            for em in email_sc:
                a = em.find('a')
                if a:
                    email.append(a['href'])
                    _dict_info['restaurant_email'] = email[1]
                else:
                    email.append('-')
                    _dict_info['restaurant_email'] = '_'
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
                geocodes.append('-,-')
            print(geocodes)
            geo_c = geocodes[0].split(',')

            for i in features_sc:
                x = i.text
                currency = x[:3]
                if currency == "LKR":
                    pass
                else:
                    features.append(x)
            print(features)

            WebDriverWait(driver2, 10)

            try:

                WebDriverWait(driver2, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@class='OTyAN _S b']"))).click()
            except:
                pass

            # Load the url
            url = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(url, 'lxml')
            WebDriverWait(driver2, 10)
            try:
                about_sc = data2.select(".jmnaM")

                price_sc = driver2.find_element(by=By.XPATH,
                                                value='//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/div[14]/div/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div[2]').text
            except:
                pass

            if about_sc:
                description.append(about_sc[0].text.lstrip())
            else:
                description.append('-')
            print(description)

            if price_sc:
                currency = price_sc[:3]
                if currency == "LKR":

                    price_range.append(price_sc.lstrip())
                else:
                    price_range.append('-')
            else:
                price_range.append('-')
            print(price_range)
            time.sleep(5)
            driver2.find_element(By.XPATH, "//div[@class='zPIck _Q Z1 t _U c _S zXWgK']").click()
            time.sleep(5)
            try:

                driver2.find_element(By.XPATH,
                                     "/html/body/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/span/span[2]").click()
            except:
                pass
            time.sleep(5)
            # Load the url
            url = driver2.page_source

            # Use bs4 to parse data from the URL
            data2 = bs4.BeautifulSoup(url, 'lxml')
            try:
                WebDriverWait(driver2, 10)
                time.sleep(5)
                dialog = driver2.find_element(by=By.XPATH, value="//div[@class='photoGridWrapper']")
                time.sleep(5)
                sc = driver2.execute_script("return document.querySelector('.photoGridWrapper').scrollHeight")
                while True:
                    driver2.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)

                    time.sleep(2)
                    dialog = driver2.find_element(by=By.XPATH, value="//div[@class='photoGridWrapper']")
                    sc_2 = driver2.execute_script("return document.querySelector('.photoGridWrapper').scrollHeight")

                    if sc_2 == sc:
                        break
                    sc = sc_2

                WebDriverWait(driver2, 5)
                time.sleep(5)
                image_sc = data2.select('.fillSquare')
                for i in image_sc:
                    img = i.find('img')
                    # if img:
                    #     images.append(img[0]['src'])
                    # else:
                    #     pass
                    if img.has_attr('src'):
                        images.append(img['src'])
                    else:
                        pass
            except:
                pass

            print(images)
            time.sleep(5)

            # get the city id
            city_id = db.select_city(city_name=row['city'])
            city = city_id
            time.sleep(5)

            dict = {'city_id': city[0], 'restaurant_name': name, 'restaurant_review_count': review_count,
                    'restaurant_address': address,
                    'restaurant_contact': contact, 'restaurant_email': email[1], 'restaurant_description': description,
                    'restaurant_website': website,
                    'restaurant_price_range': price_range, 'restaurant_geocode_lan': geo_c[0],
                    'restaurant_geocode_lon': geo_c[1]}

            df = pd.DataFrame(dict)

            # insert_df = pd.DataFrame([_dict_info])

            db.insert_data(df)

            time.sleep(5)

            # get the restaurant id
            restaurant_id = db.select_restaurant(restaurant_name=name[0])

            ids = []

            if images:
                for i in range(len(images)):
                    ids.append(restaurant_id[0])

                dict2 = {'restaurant_id': ids, 'image': images}

                df_image = pd.DataFrame(dict2)

                db.insert_images(df_image)
            else:
                pass

            # get the features
            ids2 = []

            for i in range(len(features)):
                ids2.append(restaurant_id[0])

            dict3 = {'restaurant_id': ids2, 'feature': features}

            df_feature = pd.DataFrame(dict3)

            db.insert_feature(df_feature)


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

db.save_log()
#
# time.sleep(5)
# obj.search_for_restaurants(driver=driver, city="Kandy")
# time.sleep(10)
# data = obj.scrape_restaurant_data(driver=driver, city="Kandy")
# time.sleep(10)
# if data.empty is True:
#     print("No Data")
# else:
#     time.sleep(5)
#     obj.scraping_restaurant_information(driver, data)
# driver.get("https://www.tripadvisor.com")

# time.sleep(5)
# obj.search_for_restaurants(driver=driver, city="Kandy")
# time.sleep(10)
# obj.scrape_restaurant_data(driver=driver, city="Kandy")
# time.sleep(10)
# driver.get("https://www.tripadvisor.com")
driver.quit()
