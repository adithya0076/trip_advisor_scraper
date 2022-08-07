import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd

# PATHS
SCRAPING_URL = "https://www.tripadvisor.com"
CHROME_DRIVER_PATH = "chromedriver.exe"

# INPUTS
CITY = "Ampara"
CHECK_IN = "Tue May 10 2022"
CHECK_OUT = "Wed May 11 2022"
NO_OF_PAGES = 5

# Global Variables
HOTELS_LIST = []
HOTELS_DF = None


def get_driver_object():
    """
    Creates and returns the selenium webdriver object

    Returns:
        Chromedriver object: This driver object can be used to simulate the webbrowser
    """

    # Creating the service object to pass the executable chromedriver path to webdriver
    service_object = Service(executable_path=CHROME_DRIVER_PATH)

    # Creating the ChromeOptions object to pass the additional arguments to webdriver
    options = webdriver.ChromeOptions()

    # Adding the arguments to ChromeOptions object
    options.headless = False  # To run the chrome without GUI
    options.add_argument("start-maximized")  # To start the window maximised
    options.add_argument("--disable-extensions")  # To disable all the browser extensions
    options.add_argument("--log-level=3")  # To to capture the logs from level 3 or above
    options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )  # To disable the images that are loaded when the website is opened

    # Creating the Webdriver object of type Chrome by passing service and options arguments
    driver_object = webdriver.Chrome(service=service_object, options=options)

    return driver_object


def get_website_driver(driver=get_driver_object(), url=SCRAPING_URL):
    """it will get the chromedriver object and opens the given URL

    Args:
        driver (Chromedriver): _description_. Defaults to get_driver_object().
        url (str, optional): URL of the website. Defaults to SCRAPING_URL.

    Returns:
        Chromedriver: The driver where the given url is opened.
    """

    # Opening the URL with the created driver object
    print("The webdriver is created")
    driver.get(url)
    print(f"The URL '{url}' is opened")
    return driver


def open_hotels_tab(driver):
    """ Opens the Hotels link with city provided

    Args:
        driver (Chromedriver): The driver where the url is opened.
    """
    # Finding the Input Tag for to enter the CITY name
    city_input_tag = driver.find_element(by=By.XPATH, value="//input[@placeholder='Where to?']")

    # providing the charaters in the CITY one by one as the search is dynamically loaded
    for letter in CITY:
        city_input_tag.send_keys(letter)
    time.sleep(5)

    # selecting the top search result based on the input provided
    city_input_tag.send_keys(Keys.ARROW_DOWN)
    city_input_tag.send_keys(Keys.ENTER)
    time.sleep(5)

    # selecting the type as Hotels in the webpage that is loaded
    wait = WebDriverWait(driver, 10)
    for _ in range(3):
        try:
            select_hotels_tag = wait.until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"Hotels")]')))
            driver.execute_script("arguments[0].click();", select_hotels_tag)
            break
        except:
            time.sleep(2)
            continue
    print("The Hotels window with the provided city is opened")


def select_check_in(driver):
    """The check in date is selected in the list the dates available

    Args:
        driver (Chromedriver): The driver instance where the Hotels page is loaded
    """
    # Check in Date element is selected
    check_in_dates = driver.find_elements(By.CLASS_NAME, "MNzWi")

    # Selecting the check in date in the available dates
    for date in check_in_dates:
        date_val = date.get_attribute("aria-label")
        if date_val == CHECK_IN and date.is_enabled():
            driver.execute_script("arguments[0].click();", date)
            print("Check in date selected")


def select_check_out(driver):
    """ The check out date is selected in the list the dates available

    Args:
        driver (Chromedriver): The driver instance where the check in date selected
    """
    #  After the check in date is selected the wep-page loads in the backgound the chances of getting
    #  stale element exceptions are more to avoid this we can use implicit or explicit wait

    # Selecting the Check out dates available
    wait = WebDriverWait(driver, 10)
    check_out_dates = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "MNzWi")))

    # searching the available dates and selecting the check out date
    for date in check_out_dates:
        date_val = date.get_attribute("aria-label")
        if date_val == CHECK_OUT and date.is_enabled():
            driver.implicitly_wait(10)
            # searching the check out date element in the wep page to avoid Stale Element exception
            date_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[@aria-label='{date_val}']")))
            driver.execute_script("arguments[0].click();", date_element)
            print("Check Out date selected")
            break


def select_check_in_out_dates(driver):
    """The check in and check out dates are selected in the webpage loaded

    Args:
        driver (webdriver): The driver instance where the hotels page is loaded with provided city
    """
    # Moving to the first month that is available
    time.sleep(10)
    left_button = driver.find_element(by=By.XPATH, value="//button[@class='RFOih _Z _S Q z Wc Wh _J ALXyI QNyJo']")
    if left_button.is_enabled():
        driver.execute_script("arguments[0].click();", left_button)

        # Select check in Date
    select_check_in(driver)
    time.sleep(10)

    # Select Check out Date
    select_check_out(driver)
    time.sleep(10)


def update_button(driver):
    """The check in , check out details are updated to populate the hotel results

    Args:
        driver (Chromedriver): The driver instance where check in and check out dates are selected
    """
    # The webpage is dyanmically loading in the background once check in date
    for _ in range(10):
        try:
            driver.find_element(by=By.XPATH, value='//button[@class="ui_button primary fullwidth"]').click()
            break
        except:
            time.sleep(2)
    print("The web page is loaded with the provided check in and check out dates")


def search_hotels(driver):
    """Opens the Hotels page from which the data can be parsed.

    Args:
        driver (Chromedriver): The driver where the url is opened.
    """
    # Opening the Hotels tab with the given city and waiting for it to load
    open_hotels_tab(driver)
    time.sleep(10)

    # Selecting the Check In and Check Out Dates
    select_check_in_out_dates(driver)

    # Updating the details
    update_button(driver)
    time.sleep(10)


def parse_best_offer(hotel):
    """Parse the best offer hotel details given on tripadvisor

    Args:
        hotel (Beautifulsoup object): The hotel div element which contains hotel details

    Returns:
        Dict: returns dictionary containing best offer hotel details.
    """
    hotel_name = hotel.find("a", class_="property_title").text.strip()[3:]
    hotel_price = hotel.find("div", class_="price").text
    best_price_offered_element = hotel.find("img", class_="provider_logo")
    best_price_offered_by = best_price_offered_element["alt"] if best_price_offered_element is not None else None
    review_count = hotel.find("a", class_="review_count").text
    return {
        "Hotel_Name": hotel_name,
        "Hotel_Price": hotel_price,
        "Best_Deal_By": best_price_offered_by,
        "Review_Count": review_count,
    }


def parse_other_offers(hotel, hotel_details):
    """Parse the hotel details of other deals given on tripadvisor and to the hotel_details dictionary

    Args:
        hotel (Beautifulsoup object): The hotel div element which contains hotel details
        hotel_details : Dictionary containing the best hotel details
    Returns:
        Dict: returns dictionary containing all offer's hotel details.
    """
    other_deals = hotel.find("div", class_="text-links", ).find_all("div", recursive=False)
    for i in range(3):
        try:
            deal_name_tag = other_deals[i].find("span", class_="vendorInner")
            deal_name = deal_name_tag.text if deal_name_tag is not None else None
            hotel_details[f"next_deal_{i + 1}"] = deal_name

            deal_price_tag = other_deals[i].find("div", class_="price")
            deal_price = deal_price_tag.text if deal_price_tag is not None else None
            hotel_details[f"next_deal_{i + 1}_price"] = deal_price
        except:
            hotel_details[f"next_deal_{i + 1}"] = None
            hotel_details[f"next_deal_{i + 1}_price"] = None
    return hotel_details


def parse_hotel_details(hotel):
    """Parse the hotel details from the given hotel div element

    Args:
        hotel (Beautifulsoup object): The hotel div element which contains hotel details
    """
    # declaring the global variables
    global HOTELS_LIST

    # Parsing the best offer Hotel Details
    best_offer_deals = parse_best_offer(hotel)

    # Parsing the other offers Hotel Details
    hotel_details = parse_other_offers(hotel, best_offer_deals)

    # Apending the data to the hotels list
    HOTELS_LIST.append(hotel_details)


def parse_hotels(driver):
    """ To parse th web page using the BeautifulSoup

    Args:
        driver (Chromedriver): The driver instance where the hotel details are loaded
    """
    # Getting the HTML page source
    html_source = driver.page_source

    # Creating the BeautifulSoup object with the html source
    soup = BeautifulSoup(html_source, "html.parser")

    # Finding all the Hotel Div's in the BeautifulSoup object
    hotel_tags = soup.find_all("div", {"data-prwidget-name": "meta_hsx_responsive_listing"})

    # Parsing the hotel details
    for hotel in hotel_tags:
        # condition to check if the hotel is sponsered, ignore this hotel if it is sponsered
        sponsered = False if hotel.find("span", class_="ui_merchandising_pill") is None else True
        if not sponsered:
            parse_hotel_details(hotel)
    print("The Hotels details in the current page are parsed")


def next_page(driver) -> bool:
    """To load the next webpage if it is available

    Args:
        driver (Chromedriver): The driver instance where the hotel details are loaded

    Returns:
        bool: returns True if the page is loaded
    """
    # Finding the element to load the next page
    next_page_element = driver.find_element(By.XPATH, value='.//a[@class="nav next ui_button primary"]')

    # click on the next page element if it is avialable
    if next_page_element.is_enabled():
        driver.execute_script("arguments[0].click();", next_page_element)
        time.sleep(30)
        return True
    return False


def write_to_csv():
    """To Write the hotels data in to a CSV file using pandas
    """
    # declaring the global variables
    global HOTELS_LIST, HOTELS_DF

    # Creating the pandas DataFrame object
    HOTELS_DF = pd.DataFrame(HOTELS_LIST, index=None)

    # Viewing the DataFrame
    print(f"The number of columns parsed is {HOTELS_DF.shape[1]}")
    print(f"The number of rows parsed is {HOTELS_DF.shape[0]}")

    # Conveting the DataFrame to CSV file
    HOTELS_DF.to_csv("hotels_list.csv", index=False)
    print("The CSV file is created at hotels_list.csv")


def main():
    # Create the driver and load the website
    driver = get_website_driver()

    # open the website with details provided
    search_hotels(driver)
    time.sleep(30)

    # Parse the hotel details for the given no of pages
    parse_hotels(driver)
    for page in range(NO_OF_PAGES):
        if next_page(driver):
            print(f"The next page is loaded : Page No - {page + 2}")
            parse_hotels(driver)

    # write the parsed data in to a CSV file
    write_to_csv()

    # close the driver once the parsing is completed
    driver.close()
    print("The driver is closed")


main()
