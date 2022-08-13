import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv('.env')


class BaseDB:
    def __init__(self):
        self.connection = None

    def con(self):
        try:
            connection_config_dict = {
                'host': os.environ.get("DB_HOST"),
                'user': os.environ.get("DB_USERNAME"),
                'password': os.environ.get("DB_PASSWORD"),
                'database': os.environ.get("DB_NAME"),
            }
            self.connection = mysql.connector.connect(**connection_config_dict)

            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = self.connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("Your connected to database: ", record)

        except Error as e:
            print("Error while connecting to MySQL", e)

        return self.connection

    def insert_data(self, data):
        """

        :param table_name:
        :param data:
        :return:
        """
        df = data

        query = '''INSERT INTO `restaurant`( `city_id`, `restaurant_name`, `restaurant_review_count`, `restaurant_address`, `restaurant_contact`, `restaurant_email`, `restaurant_description`,
                `restaurant_website`, `restaurant_price_range`, `restaurant_geocode_lan`, `restaurant_geocode_lon`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )'''
        for index, row in df.iterrows():
            try:
                cursor = self.connection.cursor()
                # call mysql connection and select db
                cursor.execute(query, (
                    row['city_id'], row['restaurant_name'], row['restaurant_review_count'], row['restaurant_address'],
                    row['restaurant_contact'],
                    row['restaurant_email'], row['restaurant_description'], row['restaurant_website'],
                    row['restaurant_price_range'],
                    row['restaurant_geocode_lan'], row['restaurant_geocode_lon']))
                # execute update query
                self.connection.commit()
            except Exception as error:
                print(error)

    def select_city(self, city_name):
        """

        :param city_name:
        :return:
        """
        query = '''SELECT `id` FROM `city` WHERE `city_name` = (%s)'''

        try:
            cursor = self.connection.cursor()
            # call mysql connection and select db
            cursor.execute(query, (city_name,))

            result = cursor.fetchall()
            print(result)

            return result
        except Exception as error:
            print(error)

    def select_restaurant(self, restaurant_name):
        """

        Args:
            restaurant_name:

        Returns:

        """
        query = '''SELECT `id` FROM `restaurant` WHERE `restaurant_name` = (%s)'''

        try:
            cursor = self.connection.cursor()
            # call mysql connection and select db
            cursor.execute(query, (restaurant_name,))

            result = cursor.fetchall()
            print(result)

            return result
        except Exception as error:
            print(error)

    def insert_images(self, data):
        """

        Args:
            data:

        Returns:

        """
        df = data
        query = "INSERT INTO `restaurant_image` ( `restaurant_id`, `image`) VALUES (%s, %s)"

        for index, row in df.iterrows():
            try:
                cursor = self.connection.cursor()
                # call mysql connection and select db
                cursor.execute(query, (
                    row['restaurant_id'][0], row['image']))
                # execute update query
                self.connection.commit()
            except Exception as error:
                print(error)

    def insert_feature(self, data):
        """

        Args:
            data:

        Returns:

        """
        df = data
        query = "INSERT INTO `restaurant_feature` ( `restaurant_id`, `feature_type`) VALUES (%s, %s)"

        for index, row in df.iterrows():
            try:
                cursor = self.connection.cursor()
                # call mysql connection and select db
                cursor.execute(query, (
                    row['restaurant_id'][0], row['feature']))
                # execute update query
                self.connection.commit()
            except Exception as error:
                print(error)

    def save_log(self):
        query = "SELECT `city_id`, COUNT(*) as total FROM `restaurant` GROUP BY `city_id`"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            for i in data:
                city_id = i[0]
                count = i[1]
                sql2 = "INSERT INTO `scraped_restaurants_log`( `city_id`, `no_of_restaurants_scraped`) VALUES ( %s, %s )"
                cursor.execute(sql2, (city_id, count))
                self.connection.commit()
        except Exception as e:
            print(e)
