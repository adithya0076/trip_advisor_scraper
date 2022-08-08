import mysql.connector
from mysql.connector import Error
import pandas


class BaseDB:
    def con(self):

        try:
            connection_config_dict = {
                'host': "localhost",
                'user': "root",
                'password': "",
                'database': "trip_advisor_scraped",
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
