import traceback
import mysql.connector
import json
import pandas as pd
import os
from time import gmtime, strftime
import datetime
from dotenv import load_dotenv
import re

load_dotenv()

class_name = os.path.basename(__file__)


class BaseDBModel:
    def __init__(self):

        try:
            self.mydb = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                user=os.environ.get("DB_USERNAME"),
                passwd=os.environ.get("DB_PASSWORD"),
                database=os.environ.get("DB_NAME"),
            )
            if self.mydb.is_connected():
                db_Info = self.mydb.get_server_info()
                cursor = self.mydb.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("Your connected to database: ", record)
        except Exception as error:
            traceback.print_exc()

    def base_job_handler(self, data):
        print('----------------', data.to_dict())
        current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        today = strftime("%Y-%m-%d", gmtime())
        # CHECK RESTAURANT IS AVAILABLE IN THE DATABASE OR NOT
        try:
            condition = 'restaurant_name LIKE "%s" and restaurant_geocode_lan LIKE "%s" and restaurant_geocode_lon LIKE "%s" ' % (
                data['name'][0], "%" + '{:.4f}'.format(data['restaurant_geocode_lan'][0]) + "%",
                "%" + '{:.4f}'.format(data['restaurant_geocode_lon'][0]) + "%")
            response = self.select_record("restaurant", condition)
            if response is None:
                response = self.insert_restaurant_title_data("restaurant", data)
                data["restaurant_id"] = response["id"]
                try:
                    images = self.insert_image_data("restaurant_image", data, 'image')
                except:
                    traceback.print_exc()
                try:
                    feature = self.insert_image_data("restaurant_feature", data, 'feature_type')
                except:
                    traceback.print_exc()
            else:
                # data["job_title_id"] = response["id"] if isinstance(response["id"], int) else 0
                print("Data exist in table")
        except Exception as error:
            traceback.print_exc()

        # CHECK ATTRACTION IS AVAILABLE IN THE DATABASE OR NOT
        try:

            try:
                lan = '{:.4f}'.format(float(data['attraction_geocode_lan'][0]))
                lon = '{:.4f}'.format(float(data['attraction_geocode_lon'][0]))
                condition = 'attraction_name LIKE "%s" and attraction_geocode_lan LIKE "%s" and attraction_geocode_lon LIKE "%s" ' % (
                    data['name'][0], "%" + str(lan) + "%",
                    "%" + str(lon) + "%")
            except:
                condition = 'attraction_name LIKE "%s" and attraction_geocode_lan LIKE "%s" and attraction_geocode_lon LIKE "%s" ' % (
                    data['name'][0], "%" + data['attraction_geocode_lan'][0] + "%",
                    "%" + data['attraction_geocode_lon'][0] + "%")

            response = self.select_record("attraction", condition)
            if response is None:
                response = self.insert_attraction_title_data("attraction", data)
                data["attraction_id"] = response["id"]
                try:
                    images = self.insert_image_data("attraction_image", data, 'image')
                except:
                    traceback.print_exc()

                read = data['attraction_type'][0]
                for i in read:
                    condition = 'attraction_type="%s" ' % i
                    response = self.select_record("attraction_feature_type", condition)
                    dict = {}
                    if response is None:
                        attraction_id = self.insert_feature_type("attraction_feature_type", i)
                        data['attraction_type_id'] = attraction_id["id"]
                        dict["attraction_id"] = data["attraction_id"][0]
                        dict['attraction_type_id'] = data['attraction_type_id'][0]
                        attraction_feature = self.insert_feature("attraction_feature", dict)
                    else:
                        data['attraction_type_id'] = response["id"]
                        dict["attraction_id"] = data["attraction_id"][0]
                        dict['attraction_type_id'] = data['attraction_type_id'][0]
                        attraction_feature = self.insert_feature("attraction_feature", dict)
            else:
                print("Data exist in table")

        except Exception as error:
            traceback.print_exc()

        # check attraction url is saved
        try:
            for index, row in data.iterrows():
                print("Done to process")
                condition = 'url="%s"' % (row['url'])
                response = self.select_record("attraction_url_log", condition)
                dict = {}
                if response is None:
                    dict['city'] = row['city']
                    dict['url'] = row['url']
                    response = self.insert_log("attraction_url_log", dict)
                else:
                    pass
        except:
            traceback.print_exc()

    def get_row_count(self, table_name, condition=None):
        record_row = None
        sql = "SELECT COUNT(`id`) FROM " + table_name
        if condition:
            sql += " WHERE " + condition
        self.get_cursor()
        cursor = self.mydb.cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchone()
        self.mydb.commit()
        cursor.close()
        self.mydb.close()
        if result:
            record_row = {
                "count": result[0]
            }
        return record_row

    def get_nth_row(self, table_name, list_columns, row, condition=None):
        record_row = None
        columns = ''
        for column in list_columns:
            columns = columns + "`" + column + "`,"
        sql = "SELECT " + columns + " FROM " + table_name + " LIMIT " + str(row - 1) + ",1"
        if condition:
            sql += " WHERE " + condition
        self.get_cursor()
        cursor = self.mydb.cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchone()
        self.mydb.commit()
        cursor.close()
        self.mydb.close()
        if result:
            record_row = {}
            keys = range(len(list_columns))
            for i in keys:
                record_row[list_columns[i]] = result[i]
        return record_row

    def select_record(self, table_name, condition=None):
        record_row = None
        sql = "SELECT `id` FROM " + table_name
        if condition:
            sql += " WHERE " + condition
        self.get_cursor()
        cursor = self.mydb.cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchone()
        self.mydb.commit()
        cursor.close()
        self.mydb.close()
        if result:
            record_row = {
                "id": result[0]
            }
        return record_row
        # Here returns search id for given condition

    def select_rows(self, table_name):
        try:
            query = "SELECT * FROM " + table_name
            self.get_cursor()
            cursor = self.mydb.cursor(buffered=True)
            cursor.execute(query)
            df = pd.DataFrame(cursor.fetchall(), columns = ['id', 'city', 'url'])
            cursor.close()
            self.mydb.close()
            return df
        except:
            traceback.print_exc()


    def insert_image_data(self, table_name, data, content):
        record_row = None
        data = data.to_dict()
        read = data[content][0]
        try:
            for i in read:
                insert_data = {}
                insert_data['restaurant_id'] = int(data['restaurant_id'][0])
                insert_data[content] = i.replace('"', '')

                # filtered_insert_data = self.pop_null_values(insert_data)

                last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **insert_data)
                record_row = {"id": last_id}
        except:
            pass

        try:
            for i in read:
                insert_data = {}
                insert_data['attraction_id'] = int(data['attraction_id'][0])
                insert_data[content] = i

                # filtered_insert_data = self.pop_null_values(insert_data)

                last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **insert_data)
                record_row = {"id": last_id}
        except:
            pass
        return record_row

    def insert_restaurant_title_data(self, table_name, data):
        record_row = None
        for index, row in data.iterrows():
            insert_data = {}
            insert_data['city_id'] = self.check_nun('city_id', row)
            insert_data['restaurant_name'] = self.check_nun('name', row)
            insert_data['restaurant_review_count'] = self.check_nun('restaurant_review_count', row)
            insert_data['restaurant_address'] = self.check_nun('restaurant_address', row)
            insert_data['restaurant_contact'] = self.check_nun('restaurant_contact', row)
            insert_data['restaurant_email'] = self.check_nun('restaurant_email', row)
            insert_data['restaurant_description'] = self.check_nun('restaurant_description', row)
            insert_data['restaurant_website'] = self.check_nun('restaurant_website', row)
            insert_data['restaurant_price_range'] = self.check_nun('restaurant_price_range', row)
            insert_data['restaurant_geocode_lan'] = self.check_nun('restaurant_geocode_lan', row)
            insert_data['restaurant_geocode_lon'] = self.check_nun('restaurant_geocode_lon', row)
            insert_data['source'] = self.check_nun('url', row)

            filtered_insert_data = self.pop_null_values(insert_data)

            last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **filtered_insert_data)
            record_row = {"id": last_id}
        return record_row

    def insert_feature_type(self, table_name, data):
        record_row = None
        insert_data = {}
        insert_data['attraction_type'] = data
        filtered_insert_data = self.pop_null_values(insert_data)

        last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **filtered_insert_data)
        record_row = {"id": last_id}
        return record_row

    def insert_feature(self, table_name, data):
        record_row = None
        insert_data = {}
        insert_data['attraction_id'] = int(data['attraction_id'])
        insert_data['attraction_type_id'] = int(data['attraction_type_id'])

        last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **insert_data)
        record_row = {"id": last_id}
        return record_row

    def insert_log(self, table_name, data):
        record_row = None
        insert_data = {}
        insert_data['city'] = data['city']
        insert_data['url'] = data['url']
        # filtered_insert_data = self.pop_null_values(insert_data)
        print(insert_data)
        last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **insert_data)
        record_row = {"id": last_id}
        return record_row

    def insert_attraction_title_data(self, table_name, data):
        record_row = None
        for index, row in data.iterrows():
            insert_data = {}
            insert_data['city_id'] = self.check_nun('city_id', row)
            insert_data['attraction_name'] = self.check_nun('name', row)
            insert_data['attraction_review_count'] = self.check_nun('attraction_review_count', row)
            insert_data['attraction_address'] = self.check_nun('attraction_address', row)
            insert_data['attraction_contact'] = self.check_nun('attraction_contact', row)
            insert_data['attraction_email'] = self.check_nun('attraction_email', row)
            insert_data['attraction_description'] = self.check_nun('attraction_description', row)
            insert_data['attraction_website'] = self.check_nun('attraction_website', row)
            insert_data['attraction_geocode_lan'] = self.check_nun('attraction_geocode_lan', row)
            insert_data['attraction_geocode_lon'] = self.check_nun('attraction_geocode_lon', row)
            insert_data['source'] = self.check_nun('url', row)
            filtered_insert_data = self.pop_null_values(insert_data)

            last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **filtered_insert_data)
            record_row = {"id": last_id}
        return record_row

    def insert_job_locations_data(self, table_name, data):
        record_row = None
        for index, row in data.iterrows():
            insert_data = {}
            insert_data['job_id'] = self.check_nun('job_id', row)
            insert_data['district_id'] = self.check_nun('district_id', row)
            insert_data['city_id'] = self.check_nun('city_id', row)
            insert_data['from_description'] = self.check_nun('from_description', row)

            filtered_insert_data = self.pop_null_values(insert_data)

            last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **filtered_insert_data)
            record_row = {"id": last_id}
        return record_row

    def insert_jobs_job_categories_data(self, table_name, data):
        record_row = None
        for index, row in data.iterrows():
            insert_data = {}
            insert_data['job_id'] = self.check_nun('pivot_job_id', row)
            insert_data['category_id'] = self.check_nun('pivot_category_id', row)

            filtered_insert_data = self.pop_null_values(insert_data)

            last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **filtered_insert_data)
            record_row = {"id": last_id}
        return record_row

    def insert_job_data(self, table_name, data):
        for index, row in data.iterrows():
            insert_data = {}
            insert_data['user_id'] = self.check_nun('user_id', row)
            insert_data['platform_type'] = self.check_nun('platform', row)
            insert_data['job_source'] = self.check_nun('job_source_name', row)
            insert_data['is_remote'] = self.check_nun('is_remote', row)
            insert_data['unique_key'] = self.check_nun('unique_key', row)
            insert_data['platform_id'] = self.check_nun('company_id', row)
            insert_data['work_place'] = self.check_nun('work_place', row)
            insert_data['description'] = self.check_nun('job_description', row)
            insert_data['ocr_description'] = self.check_nun('job_description_json', row)
            insert_data['description_html'] = self.check_nun('description_html', row)
            insert_data['posting_language'] = self.check_nun('description_language', row)
            insert_data['description_image_path'] = self.check_nun('s3_url_job_poster', row)
            insert_data['email'] = self.check_nun('company_email', row)
            insert_data['telephone'] = self.check_nun('company_telephone', row)
            insert_data['currency'] = self.check_nun('currency', row)
            insert_data['min_salary'] = self.check_nun('min_salary', row)
            insert_data['educational_requirements'] = self.check_nun('educational_requirements', row)
            insert_data['max_salary'] = self.check_nun('max_salary', row)
            insert_data['job_link'] = self.check_nun('job_link', row)
            insert_data['career_page_url'] = self.check_nun('career_page_url', row)
            insert_data['job_title_id'] = self.check_nun('job_title_id', row)
            insert_data['job_type_id'] = self.check_nun('job_type_id', row)
            insert_data['start_at'] = self.check_nun('start_at', row)
            insert_data['expire_at'] = self.check_nun('closing_date', row)
            insert_data['is_valid_expire_date'] = self.check_nun('is_valid_expire_date', row)
            insert_data['is_active'] = self.check_nun('is_active', row)
            insert_data['no_of_vacanci'] = self.check_nun('no_of_vacanci', row)
            insert_data['slug'] = self.check_nun('slug', row)
            insert_data['created_at'] = self.check_nun('created_at', row)
            insert_data['updated_at'] = self.check_nun('updated_at', row)

            filtered_insert_data = self.pop_null_values(insert_data)
            last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **filtered_insert_data)
            record_row = {"id": last_id}

            # INDEX NEW INSERTED JOB IN GOOGLE
            self.helper.index_job_in_google(record_row['id'])

            return record_row

    def check_nun(self, key, row):
        key_val = row[key] if key in row else ''
        key_val = str(key_val)
        key_val.replace('[', '').replace(']', '').replace('nan', '').replace('None', '')
        return key_val if not pd.isnull(key_val) else ''

    def pop_null_values(self, insert_dict):
        key_list = list(insert_dict.keys())
        for key in key_list:
            if insert_dict[key] == '' or insert_dict[key] == 'None':
                insert_dict.pop(key)
        return insert_dict

    def common_routing_insert_dictionary_data_to_db(self, table_name=None, **insert_data):
        if not table_name:
            return False
        else:
            cursor = None
            try:
                self.get_cursor()
                cursor = self.mydb.cursor()
            except Exception as error:
                print(error)
            # prepare values in the string for mysql
            # copy the original dictionary to working
            insert_data_working_dic = insert_data.copy()
            for dic_key in list(insert_data_working_dic):
                # This is to check if there is a dictionary within a dictionary
                # This only works by checking value of the key pair
                temp_value = insert_data_working_dic[dic_key]
                if isinstance(temp_value, (dict, list)):
                    # We will use json.dumpt to qualify the incoming data
                    json_val = json.dumps(insert_data_working_dic[dic_key], ensure_ascii=False)
                    # validate it
                    isValid = self.json_validator(json_val)
                    del (insert_data_working_dic[dic_key])
                    # now insert back JSon format to the dictionary
                    insert_data_working_dic.update({dic_key: json_val})
            # add %s for every columns names as placeholders
            query_placeholders = ', '.join(['%s'] * len(insert_data_working_dic))
            # add ',' between every columns
            query_columns = ', '.join(insert_data_working_dic)
            query_columns = query_columns.replace('nan', '')
            # create values list
            list_of_values = [insert_data_working_dic[key] for key in insert_data_working_dic]
            # print("\n", list_of_values)
            # genarate query with given details
            query = ''' INSERT INTO %s (%s) VALUES (%s) ''' % (table_name, query_columns, query_placeholders)
            last_insert_id = None
            try:
                cursor.execute(query, list_of_values)
                self.mydb.commit()
                last_insert_id = cursor.lastrowid
                cursor.close()
                self.mydb.close()
            except Exception as error:
                print(error)
            return last_insert_id

    def update_multiple_records(self, table_name, update_columns, search_key, update_ids):
        if (len(update_ids) == 1):
            query = "UPDATE %s SET %s WHERE %s IN (%s)" % (table_name, update_columns, search_key, update_ids[0])
        else:
            query = "UPDATE %s SET %s WHERE %s IN %s" % (table_name, update_columns, search_key, update_ids)
        try:
            self.get_cursor()
            cursor = self.mydb.cursor()
            # call mysql connection and select db
            cursor.execute(query)
            # execute update query
            self.mydb.commit()
            cursor.close()
            self.mydb.close()
        except Exception as error:
            print(error)

    def update_multiple_records_two(self, table_name, update_columns, condition):
        query = "UPDATE %s SET %s WHERE %s" % (table_name, update_columns, condition)
        try:
            self.get_cursor()
            cursor = self.mydb.cursor()
            # call mysql connection and select db
            cursor.execute(query)
            # execute update query
            self.mydb.commit()
            cursor.close()
            self.mydb.close()
        except Exception as error:
            print(error)

    def select_data(self, table_name, fields, condition='1', group='', order='', limit=''):
        return_list = []
        query_columns = ', '.join(fields)
        # Add fields condition order by group by and limit as dynamically for the select query
        query = '''SELECT %s FROM %s WHERE %s %s %s %s''' % (query_columns, table_name, condition, group, order, limit)
        self.get_cursor()
        my_cursor = self.mydb.cursor()
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        self.mydb.commit()
        my_cursor.close()
        self.mydb.close()
        if not result:
            return []
        else:
            for row in result:
                record_row = {}
                i = 0
                for key_val in fields:
                    if "as" in key_val:
                        # "count(`source`) as val" Here need to add val as
                        # field name below lines for this converting
                        x = key_val.split(' as ')
                        key_val = x[1] if len(x) > 1 else key_val
                        key_val = key_val.strip()
                    record_row[key_val] = row[i]
                    i = i + 1
                return_list.append(record_row)
        return return_list

    def delete_record(self, table_name, condition=1):
        query = "DELETE FROM %s WHERE %s" % (table_name, condition)
        self.get_cursor()
        cursor = self.mydb.cursor()
        cursor.execute(query)
        last_delete_id = cursor.lastrowid
        self.mydb.commit()
        cursor.close()

    def get_cursor(self):
        if self.mydb.is_connected():
            pass
        else:
            # reconnect your cursor as you did in __init__ or wherever
            self.__init__()
        return True

    def json_validator(self, data):
        try:
            json.loads(data)
            return True
        except:
            return False
