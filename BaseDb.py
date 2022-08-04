import mysql.connector
from mysql.connector import Error
import pandas as pd


class BaseDB:

    def con(self):

        cursor = None

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


# obj = BaseDB()
# con = obj.con()
# cursor = con.cursor()
# df = pd.read_csv("cities.csv")
# sql = "INSERT INTO `city` (`id`, `city_name`) VALUES (%s,%s)"
# for index, row in df.iterrows():
#     cursor.execute(sql, (row['id'], row['name_en']))
#     con.commit()
#     print(row['name_en'])
