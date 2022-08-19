import traceback
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time


class SeleniumHelper:
    def __init__(self):
        self.GECKO_DRIVER_PATH = "./driver/geckodriver"
        # self.GECKO_DRIVER_PATH = "E:\codes\Django\scraping\helpers\geckodriver.exe"

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
        try:
            driver.get(self.SCRAPING_URL)
            print(f"The URL '{self.SCRAPING_URL}' is opened ")
        except:
            traceback.print_exc()
            driver.quit()

        return driver

    def check_connection(self):
        connection = False
        try_count = 1
        while not connection:
            try:
                var = requests.get('https://www.google.com/', timeout=30).status_code
                connection = True
                print("Internet connected...")
            except:
                connection = False
                print("No internet connection... Check count: ", try_count)
                time.sleep(5)
                try_count += 1

    def find_xpath_element(self, driver, xpath, is_get_text=False):
        try:
            if is_get_text:
                return True, driver.find_element(by=By.XPATH, value=xpath).text
            else:
                return True, driver.find_element(by=By.XPATH, value=xpath)
        except:
            return False, None

    def driver_execute(self, driver, program):
        try:
            driver.execute_script(program)
        except:
            traceback.print_exc()

    def sleep_time(self, val):
        time.sleep(val)
