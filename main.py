from sources.trip_advisor_restaurants_scraper import TripAdvisorRestaurantScraper
from helpers.selenium_helper import SeleniumHelper
from sources.dbModel.BaseDb import BaseDB
import pandas as pd
import time

obj1 = SeleniumHelper()
driver = obj1.getdriver()
db = BaseDB()
obj = TripAdvisorRestaurantScraper(obj1,db)

df = pd.read_csv("datasets/cities.csv")

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


driver.quit()
