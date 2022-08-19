import traceback

from sources.trip_advisor_restaurants_scraper import TripAdvisorRestaurantScraper
from sources.trip_advisor_attractions_scraper import TripAdvisorAttractionsScraper
from helpers.selenium_helper import SeleniumHelper
from sources.dbModel.BaseDBModel import BaseDBModel
import pandas as pd
import time
import urllib



db = BaseDBModel()
df = pd.read_csv("datasets/cities.csv")


# obj = TripAdvisorRestaurantScraper(obj1, db)
# for index, row in df.iterrows():
#     time.sleep(5)
#     obj.search_for_restaurants(driver=driver, city=row['name_en'])
#     time.sleep(10)
#     data = obj.scrape_restaurant_data(driver=driver, city=row['name_en'])
#     time.sleep(10)
#     if data.empty is True:
#         print("No Data")
#     else:
#         time.sleep(5)
#         obj.scraping_restaurant_information(driver, data)
#     driver.get("https://www.tripadvisor.com")
#     if index == 6:
#         break
#     # db.save_log()
obj1 = SeleniumHelper()
obj1.check_connection()
driver = obj1.getdriver()
attraction = TripAdvisorAttractionsScraper(obj1, db)
for index, row in df.iterrows():
    attraction.search_for_attractions(driver=driver, city=row['name_en'])
    time.sleep(10)
    data = attraction.scrape_attraction_data(driver=driver, city=row['name_en'])
    if data.empty is True:
        print("No Data")
    else:
        time.sleep(5)
        attraction.scraping_attraction_information(driver, data)
    obj1.check_connection()
    driver.get("https://www.tripadvisor.com")
driver.quit()

