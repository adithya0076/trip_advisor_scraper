import json

import selenium
import io
import requests
import bs4
import urllib.request
import urllib.parse
import pandas as pd
import re

import time
from selenium import webdriver

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from mysql.connector import Error
from BaseDb import BaseDB

# PATHS
SCRAPING_URL = "https://www.tripadvisor.com"
GECKO_DRIVER_PATH = "geckodriver.exe"

# Database Connection
db = BaseDB()
con = db.con()
cursor = con.cursor()


def get_driver():
    """

    Creating and returning the selenium webdriver.

    Uses firefox and the geckodriver.
    :return driver_object:

    Returns:
         Geckodriver object: This driver object is used to simulate the firefox browser.
    """

    # Creating the service object to pass the executable geckodriver path to webdriver
    service_obj = Service(executable_path=GECKO_DRIVER_PATH)
    profile_path = r'C:\Users\sinxdell\AppData\Roaming\Mozilla\Firefox\Profiles\2lfh6wg7.default-release'
    # profile_path2 = r'C:\Users\sinxdell\AppData\Local\Google\Chrome\User Data\Default'
    # Creating the Firefox options to add the additional options to the webdriver
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('ignore-ssl-errors')
    options.set_preference('profile', profile_path)
    driver = Firefox(options=options, service=service_obj)
    driver.maximize_window()
    print('Webdriver is created')

    # caps = DesiredCapabilities.CHROME
    # profile_path2 = r'C:\Users\sinxdell\AppData\Local\Google\Chrome\User Data\Default'
    # caps['goog:loggingPrefs'] = {"performance": "ALL", "browser": "ALL"}
    # options = Options()
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--ignore-certificate-errors')
    # options.set_preference('profile', profile_path2)
    # options.add_argument('ignore-ssl-errors')
    # driver = webdriver.Chrome(desired_capabilities=caps,options=options, executable_path="chromedriver.exe")
    # driver.maximize_window()
    return driver


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response


def processLog(log, driver):
    log = json.loads(log["message"])["message"]
    if ("Network.responseReceived" in log["method"] and "params" in log.keys()):
        body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': log["params"]["requestId"]})
        return log["params"]


def get_driver_object(driver=get_driver(), url=SCRAPING_URL):
    """
    This function will get the driver object and url as parameters and opens the given URL.

    Args:
        driver (Geckodriver): _description_. Defaults to get_driver().
        url (str, optional): URL of the website. Defaults to SCRAPING_URL.

    Returns:
        Geckodriver: The driver where the given url is opened.

    :param driver:
    :param url:
    :return driver:

    """

    # opening the URL
    driver.get(url)
    print(f"The URL '{url}' is opened ")
    return driver


def search_for_hotels(driver, city):
    """
    This function opens the hotels page from the home screen and the search for the city.

    Args:
        driver (Geckodriver): The driver where the url is opened.
        city: The city to which to be searched.
    :param driver:
    :param city:

    """
    # Finds the hotel page button
    driver.find_element(by=By.XPATH, value="//a[@href='/Hotels']").click()

    l = driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/form/input[1]")
    l.send_keys(city)
    WebDriverWait(driver, 10)
    time.sleep(5)
    l.send_keys(Keys.ENTER)
    time.sleep(5)
    print(f"The city: '{city}' is searched")


def save_hotel_images():
    """

    :param data:
    :return:
    """
    sql = "SELECT `id` FROM `hotel` WHERE `hotel_name` = %s "
    data = pd.read_csv("hotels_images.csv")
    for index, row in data.iterrows():
        adr = (row['hotel'],)
        print(adr)
        if adr[0] == 'hotel':
            pass
        else:
            try:

                cursor.execute(sql, adr)
                hotel = cursor.fetchall()
                hotel_id = hotel[0]
                print(hotel_id[0])
                sql2 = "INSERT INTO `hotel_image`( `hotel_id`, `image` ) VALUES ( %s, %s )"
                cursor.execute(sql2, (hotel_id[0], row['image']))
                con.commit()
            except Exception as e:
                print(e)

    print('Image Saved')


def save_hotel_features():
    """

    :param data:
    :return:
    """
    sql = "SELECT `id` FROM `hotel` WHERE `hotel_name` = %s "
    data = pd.read_csv("hotels_features.csv")
    for index, row in data.iterrows():
        adr = (row['hotel'],)
        print(adr)
        if adr[0] == 'hotel':
            pass
        else:
            try:
                cursor.execute(sql, adr)
                hotel = cursor.fetchall()
                hotel_id = hotel[0]
                print(hotel_id[0])
                sql2 = "INSERT INTO `hotel_feature`( `hotel_id`, `feature_type` ) VALUES ( %s, %s )"
                cursor.execute(sql2, (hotel_id[0], row['feature']))
                con.commit()
            except Exception as e:
                print(e)
    print('Feature Saved')


def scrape_hotel_information(driver, data):
    """

    :param driver:
    :param data:
    :return:
    """

    driver2 = driver
    address = []
    contact = []
    description = []
    website = []
    star = []
    hotel = []
    geocodes = []

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
        read1 = data2.select(".fHvkI.PTrfg")  # address
        read2 = data2.select(".zNXea.NXOxh.NjUDn")  # contact
        read3 = data2.select("._T.FKffI.IGtbc.Ci")  # description
        read4 = data2.select(".YnKZo.Ci.Wc._S.C.pInXB._S.ITocq.jNmfd")  # website
        read5 = data2.select(".JXZuC.d.H0")  # class
        read6 = data2.select(".yplav.f.ME.H3._c")  # amenities
        read7 = data2.select(".klpje")  # geocodes

        # address = []
        # for i in range(len(read1)):
        #     x = read1[i].text
        #     x = x.lstrip()
        #     address.append(x)

        if read1:
            address.append(read1[0].text.lstrip())
        else:
            address.append('-')
        print(address)

        if read2:
            contact.append(read2[0].text.lstrip())
        else:
            contact.append('-')

        # for i in read2:
        #     x = i.text
        #     if x is None:
        #         contact.append('-')
        #     else:
        #         x = x.lstrip()
        #         contact.append(x)
        print(contact)

        # description = []
        # for i in read3:
        #     x = i.text
        #     x = x.lstrip()
        #     description.append(x)

        if read3:
            description.append(read3[0].text.lstrip())
        else:
            description.append('-')
        print(description)

        if read4:
            website.append(read4[0]['href'])
        else:
            website.append('-')
        # for i in read4:
        #     x = i['href']
        #     if x is None:
        #         website.append('-')
        #     else:
        #         x = x.lstrip()
        #         website.append(x)
        print(website)

        if read5:
            star_count = read5[0]['aria-label'].split()
            star.append(star_count[0].lstrip())
        else:
            star.append('-')

        # star = []
        # for i in read5:
        #     x = i['aria-label']
        #     x = x.split()
        #     x = x[0]
        #     x = x.lstrip()
        #     star.append(x)
        print(star)

        amenities = []
        for read in read6:
            x = read.getText().lstrip()
            amenities.append(x)

        print('features', amenities)

        dict3 = {'hotel': row['hotel'], 'feature': amenities}

        dd = pd.DataFrame(dict3)
        print(dd)
        dd.to_csv("hotels_features.csv", mode='a', header=True)

        if read7:
            geo = read7[0]['src'].lstrip()
            codes = re.search(r'center=(.*?)&', geo).group(1)
            print(codes)
            geocodes.append(codes)
        else:
            geocodes.append('-')
        WebDriverWait(driver2, 10)

        try:

            try:
                driver2.find_element(by=By.XPATH, value="//span[@class='is-shown-at-tablet krMEp b']").click()
                time.sleep(10)
                # driver2.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div[1]/div[1]/div[2]/div[3]/div/div/div/div/div[1]/div/div[1]/div/div[5]/div").click()
                WebDriverWait(driver2, 5)
                time.sleep(10)
                # driver2.find_element(by=By.XPATH, value="//div[@class='UjksM t s _U l Y']").click()

                time.sleep(10)
                # images

                # pictures
                dialog = driver2.find_element(by=By.XPATH, value="//div[@class='SPERR _R z']")
                driver2.find_element(by=By.XPATH,
                                     value="//button[@class='OKHdJ z Pc PQ Pp PD W _S Gn Z B2 BF _M PQFNM wSSLS']").click()
                try:

                    driver2.find_element(by=By.XPATH,
                                         value="//span[@class='whtrm _G z u Pi PW Pv PI _S Wh Wc B- Dtjvh'] ").click()
                except:
                    print('ok')

                # Scroll down
                driver2.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight/2", dialog)

                time.sleep(10)
                WebDriverWait(driver2, 5)

                # Load the url
                url1 = driver2.page_source

                # Use bs4 to parse data from the URL
                data3 = bs4.BeautifulSoup(url1, 'lxml')
                time.sleep(5)
                for items in data3.select(".cfCAA.w._Z.GA"):
                    image = items['style'].split("url(")[1].split(")")[0]
                    images.append(image)

                print('images', images)
                WebDriverWait(driver2, 5)
                time.sleep(10)
            except:
                print('Error')


        except:

            # try:
            driver2.find_element(by=By.XPATH,
                                 value="//button[@class='RFOih _Z _S Q z Wc Wh _J gUFiK vuowK']").click()
            # except:
            #     driver2.find_element(by=By.XPATH, value="//button[@class='RFOih _Z _S Q z Wc Wh _J gUFiK']").click()
            time.sleep(5)
            try:
                driver2.find_element(by=By.XPATH, value="//span[@class='is-shown-at-tablet krMEp b']").click()
                time.sleep(10)
                # driver2.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div[1]/div[1]/div[2]/div[3]/div/div/div/div/div[1]/div/div[1]/div/div[5]/div").click()
                WebDriverWait(driver2, 5)
                time.sleep(10)
                # driver2.find_element(by=By.XPATH, value="//div[@class='UjksM t s _U l Y']").click()

                time.sleep(10)
                # images

                # pictures
                dialog = driver2.find_element(by=By.XPATH, value="//div[@class='SPERR _R z']")
                driver2.find_element(by=By.XPATH,
                                     value="//button[@class='OKHdJ z Pc PQ Pp PD W _S Gn Z B2 BF _M PQFNM wSSLS']").click()
                try:

                    driver2.find_element(by=By.XPATH,
                                         value="//span[@class='whtrm _G z u Pi PW Pv PI _S Wh Wc B- Dtjvh'] ").click()
                except:
                    print('ok')

                # Scroll down
                driver2.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight/2", dialog)

                time.sleep(10)
                WebDriverWait(driver2, 5)

                # Load the url
                url1 = driver2.page_source

                # Use bs4 to parse data from the URL
                data3 = bs4.BeautifulSoup(url1, 'lxml')
                time.sleep(5)
                for items in data3.select(".cfCAA.w._Z.GA"):
                    image = items['style'].split("url(")[1].split(")")[0]
                    images.append(image)

                print('images', images)
                WebDriverWait(driver2, 5)
                time.sleep(10)
            except:
                print('Error')

        hotel.append(row['hotel'])

        dict2 = {'hotel': row['hotel'], 'image': images}

        du = pd.DataFrame(dict2)
        print(du)
        if du.empty == True:
            print('No Images')
        else:
            du.to_csv("hotels_images.csv", mode='a', header=True)
        WebDriverWait(driver2, 10)
        # if index == 2:
        #     break

    dict = {'hotel': hotel, 'address': address, 'contact': contact, 'description': description,
            'website': website, 'class': star, 'geocodes': geocodes}

    df = pd.DataFrame(dict)
    print(df)
    # df.to_csv("hotels_srcs.csv")

    return df


def scraping_hotels_data(driver, city):
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

    # Elements which are selected
    read1 = data.select(".listing_title")
    read2 = data.select(".price-wrap")
    read3 = data.select(".review_count")

    urls = []

    for read in read1:
        a = read.find('a')
        if a.is_empty_element:
            print('None')
        else:
            link = 'https://www.tripadvisor.com/' + a['href'] + ''
            urls.append(link)

    name = []
    for i in range(len(read1)):
        x = read1[i].text
        x = x.lstrip()
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

    # reviews = [i.text.split()[0] for i in read3]
    reviews = []
    for i in read3:
        x = i.text
        x = x.split()
        reviews.append(x[0])
    print(reviews)

    # Creating a dictionary to send it to the dataframe

    dict = {'city': city, 'hotel': name, 'price': price, 'review_count': reviews}
    df = pd.DataFrame(dict)
    df.style.set_table_attributes("style='display:inline'").set_caption(city)

    url1 = driver.current_url

    dict2 = {'city': city, 'hotel': name, 'url': urls, }
    fd = pd.DataFrame(dict2)

    fd.to_csv("hotels_url.csv", mode='w', header=True)

    # data = {
    #     'df': df,
    #     'fd': fd,
    # }

    return df


def write_to_csv(data, data2):
    """
    Writes the pandas dataframe into a csv file in file directory.

    Args:
        data (Pandas DataFrame): The driver where the url is opened.

    :param data2:
    :param data:

    """

    # Writing data into a csv

    df = data
    hq = data2
    sql2 = "SELECT `id` FROM `city` WHERE `city_name` = %s "
    df_merged = pd.merge(df, hq, on='hotel')
    print(df_merged)
    # df_merged.to_csv("hotels_all.csv", mode='w', header=True)
    sql = "INSERT INTO `hotel` ( `city_id`, `hotel_name`, `hotel_price`, `hotel_review_count`, `hotel_address`, `hotel_contact`, `hotel_description`, `hotel_website`, `hotel_class`, `hotel_geocode_lat`, `hotel_geocode_lon` ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:

        for index, row in df_merged.iterrows():
            try:
                adr = (row['city'],)
                cursor.execute(sql2, adr)
                print('Done2')
                city = cursor.fetchall()
                print(type(city), city)
                city_id = city[0]
                print(city_id[0])
                geocodes = row['geocodes'].split(',')
                cursor.execute(sql, (
                    city_id[0], row['hotel'], row['price'], row['review_count'], row['address'], row['contact'],
                    row['description'], row['website'], row['class'], geocodes[0], geocodes[1]))
                con.commit()
            except Exception as e:
                print(e)
        print("done")
    except Error as e:
        print('Error', e)

    # if data is None:
    #     print('No Data Recorded')
    # else:
    #     data.to_csv("hotels_list.csv", mode='a', header=True)

    time.sleep(5)

    save_hotel_images()

    save_hotel_features()


def save_hotel_log():
    sql = "SELECT `city_id`, COUNT(*) as total FROM `hotel` GROUP BY `city_id`"
    cursor.execute(sql)
    hotel = cursor.fetchall()
    print(hotel)
    for i in hotel:
        city_id = i[0]
        count = i[1]
        sql2 = "INSERT INTO `scraped_hotel_log`( `city_id`, `no_of_hotels_scraped`) VALUES ( %s, %s )"
        cursor.execute(sql2, (city_id, count))
        con.commit()

    print('Log Saved')


def main():
    # Read Data from the csv
    driver = get_driver_object()

    df = pd.read_csv("cities.csv")
    for index, row in df.iterrows():
        # print(row['name_en'])

        # Create the driver

        time.sleep(5)

        # Searching for hotels
        search_for_hotels(driver=driver, city=row['name_en'])
        time.sleep(10)
        WebDriverWait(driver, 10)
        # Scraping the hotels data
        data = scraping_hotels_data(driver, city=row['name_en'])
        print(data)

        if data.empty is True:
            print("No data")
        else:
            # Writes the dataframe into a csv
            time.sleep(10)
            urls = pd.read_csv("hotels_url.csv")
            data2 = scrape_hotel_information(driver, urls)
            time.sleep(5)
            write_to_csv(data, data2)

        time.sleep(10)
        driver.get(SCRAPING_URL)
        if index == 6:
            break
    WebDriverWait(driver, 5)
    save_hotel_log()
    driver.quit()


main()
