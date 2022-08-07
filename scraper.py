import re
from telnetlib import EC

import selenium
import io
import requests
import bs4
import urllib.request
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from _datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# options = webdriver.ChromeOptions()
# options.add_experimental_option("detach", True)
# options.headless = False
# prefs = {"profile.default_content_setting_values.notifications": 2}
# options.add_experimental_option("prefs", prefs)
#
# driver = webdriver.Chrome("chromedriver.exe", options=options)
from selenium.webdriver.support.wait import WebDriverWait

options = FirefoxOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('ignore-ssl-errors')
profile = webdriver.FirefoxProfile()
driver = webdriver.Firefox(firefox_profile=profile, options=options, executable_path="driver/geckodriver.exe")

driver.maximize_window()

driver.get("https://www.tripadvisor.com")
time.sleep(5)
driver.find_element(by=By.XPATH, value="//a[@href='/Hotels']").click()

l = driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/form/input[1]")
l.send_keys("Ampara")
WebDriverWait(driver, 10)

time.sleep(5)
# first_dropdown_element = driver.find_element(by=By.XPATH, value='//div[@id = "typeahead_results"]/a')
# city_url = first_dropdown_element.get_attribute('href')
# print('--------', city_url)

# # l.send_keys(Keys.ARROW_DOWN)
l.send_keys(Keys.ENTER)

time.sleep(10)
url = driver.page_source

data = bs4.BeautifulSoup(url, 'lxml')

read1 = data.select(".listing_title")
read2 = data.select(".price-wrap")

name = []
for i in range(len(read1)):
    x = read1[i].text
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



dict = {'hotel': name, 'price': price}
df = pd.DataFrame(dict)
print(df)
df.to_csv("hotels_list.csv", header=True)
