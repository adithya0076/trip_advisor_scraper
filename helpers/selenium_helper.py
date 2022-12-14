import traceback
import requests
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from wasabi import msg
from selenium.webdriver.support import expected_conditions as EC

import time


class SeleniumHelper:
    def __init__(self):
        self.GECKO_DRIVER_PATH = "./driver/geckodriver"
        # self.GECKO_DRIVER_PATH = "E:\codes\Django\scraping\helpers\geckodriver.exe"
        self.is_server = 1
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
        if self.is_server == 1:
            self.profile.set_preference("browser.cache.disk.enable", False)
            self.profile.set_preference("browser.cache.memory.enable", False)
            self.profile.set_preference("browser.cache.offline.enable", False)
            self.profile.set_preference("network.http.use-cache", False)
            # self.options.add_argument('--headless')

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

    def find_xpath_elements(self, driver, xpath, is_get_text=False):
        try:
            if is_get_text:
                return True, driver.find_elements(by=By.XPATH, value=xpath).text
            else:
                return True, driver.find_elements(by=By.XPATH, value=xpath)
        except:
            return False, None
    def driver_execute(self, driver, program):
        try:
            driver.execute_script(program)
        except:
            traceback.print_exc()

    def sleep_time(self, val):
        time.sleep(val)

    def click_xpath(self, driver, xpath):
        try:
            driver.find_element(by=By.XPATH, value=xpath).click()
            msg.good('click_xpath pass')
            return True
        except:
            msg.fail('click_xpath fail')
            return False

    def find_elements_by_xpath(self, main_element, xpath, webdriver_wait, multy_elements=True, is_wait=True):
        try:
            self.wait_for_xpath_load(webdriver_wait, xpath) if is_wait else None
            if multy_elements:
                found_element = main_element.find_elements(By.XPATH, xpath)
            else:
                found_element = main_element.find_element(By.XPATH, xpath)
            msg.good('find_elements_by_xpath success')
            return found_element
        except:
            msg.fail('find_elements_by_xpath fail')
            return False

    def driver_scroll_down(self, web_driver, scroll_count=int, y_down=int, waiting_time=float):
        try:
            msg.info('driver_scroll_down start')
            for i in tqdm(range(scroll_count)):
                from_no = 0
                web_driver.execute_script("window.scrollTo(" + str(from_no) + ", " + str(i * y_down) + ")")
                time.sleep(float(waiting_time))
                from_no += y_down
            msg.info('driver_scroll_down finish')
            return True
        except:
            msg.fail('driver_scroll_down fail')
            return False