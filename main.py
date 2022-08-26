import traceback

from sources.trip_advisor_restaurants_scraper import TripAdvisorRestaurantScraper
from sources.trip_advisor_attractions_scraper import TripAdvisorAttractionsScraper
from sources.trip_advisor_hotels_scraper import TripAdvisorHotelsScraper
from helpers.selenium_helper import SeleniumHelper
from sources.dbModel.BaseDBModel import BaseDBModel
import pandas as pd
import time
import urllib



db = BaseDBModel()
df = pd.read_csv("datasets/cities.csv")

# obj1 = SeleniumHelper()
# obj1.check_connection()
# driver = obj1.getdriver()
# attraction = TripAdvisorAttractionsScraper(obj1, db)
# attraction.search_for_attractions(driver=driver, city="Sri Lanka")
# time.sleep(10)
# attraction.scrape_attraction_data(driver=driver, city="Sri Lanka")
# condition = 'type_id="%s" ' % 3
# data = db.select_rows("url_log", condition)
# print(data)
# if data.empty is True:
#     print("No Data")
# else:
#     time.sleep(5)
#     attraction.scraping_attraction_information(driver, data)
# obj1.check_connection()
# driver.get("https://www.tripadvisor.com")


# obj1 = SeleniumHelper()
# obj1.check_connection()
# driver = obj1.getdriver()
# hotel = TripAdvisorHotelsScraper(obj1, db)
# # hotel.search_for_hotels(driver=driver, city="Sri Lanka")
# # time.sleep(10)
# # hotel.scrape_hotel_data(driver=driver, city="Sri Lanka")
# condition = 'type_id="%s" ' % 2
# data = db.select_rows("url_log", condition)
# print(data)
# if data.empty is True:
#     print("No Data")
# else:
#     time.sleep(5)
#     hotel.scraping_hotel_information(driver, data)
# obj1.check_connection()
# driver.get("https://www.tripadvisor.com")


obj1 = SeleniumHelper()
obj1.check_connection()
driver = obj1.getdriver()
restaurant = TripAdvisorRestaurantScraper(obj1, db)
restaurant.search_for_restaurants(driver=driver, city="Sri Lanka")
time.sleep(10)
# url = restaurant.traverse_through_cities(driver=driver)
# restaurant.traverse_through_cities_pagination(driver=driver, current_url='https://www.tripadvisor.com/Restaurants-g293961-Sri_Lanka.html#LOCATION_LIST')
condition = 'type_id="%s" ' % 1
data = db.select_rows("url_log", condition)
print(data)
if data.empty is True:
    print("No Data")
else:
    time.sleep(5)
    restaurant.scraping_restaurant_information(driver, data)
obj1.check_connection()
driver.get("https://www.tripadvisor.com")


driver.quit()

