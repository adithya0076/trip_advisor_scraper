import traceback
import mysql.connector
import json
import pandas as pd
import os
from time import gmtime, strftime
import datetime
from dotenv import load_dotenv
import re
from helpers.Helper import Helper
import ast
from bs4 import BeautifulSoup
from app import get_base_path

load_dotenv()

class_name = os.path.basename(__file__)


class BaseDBModel:
    def __init__(self):
        self.helper = Helper()
        try:
            self.mydb = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                user=os.environ.get("DB_USERNAME"),
                passwd=os.environ.get("DB_PASSWORD"),
                database=os.environ.get("DB_NAME"),
                port=os.environ.get("DB_PORT"))
        except Exception as error:
            traceback.print_exc()

    def base_job_handler(self, data):
        print('----------------', data.to_dict())
        current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        today = strftime("%Y-%m-%d", gmtime())
        for index, row in data.iterrows():
            data["created_at"] = current_time
            data["updated_at"] = current_time
            try:
                data["is_active"][index]
            except:
                data["is_active"] = 1

            try:
                data["location"][index]
            except:
                data["location"] = ''

            try:
                data["district"][index]
            except:
                data["district"] = ''

            try:
                data["min_salary"][index]
            except:
                data["min_salary"] = ''

            try:
                data["max_salary"][index]
            except:
                data["max_salary"] = ''

            try:
                data["job_type"][index]
            except:
                data["job_type"] = ''

            # CREATE CLOSING DATE
            format_closing_date = '%Y-%m-%d'
            datetime_obj = datetime.datetime.strptime(today, format_closing_date)
            closing_date = datetime_obj + datetime.timedelta(days=14)
            closing_date = closing_date.date()

            # ADD 7 DAY EXPIRE DATE FOR ALL SCRAPED JOBS
            data["is_valid_expire_date"] = 0
            data["closing_date"] = closing_date

            # WHEN EMAIL WAS NOT FOUND TRY TO GET EMAIL FROM JOB DESCRIPTION
            try:
                try:
                    email = data['company_email'][index]
                except:
                    email = None
                if not email:
                    description_list = []
                    description_list.append(str(data['job_description'][index]) if 'job_description' in data else '')
                    description_list.append(str(data['job_description_json'][index]) if 'job_description_json' in data else '')
                    print('LEN description_list : ', len(description_list))
                    for description in description_list:
                        email = self.helper.email_finder(description)
                        print('COMPANY EMAIL FROM REGEX : ', email)
                        if email:
                            data['company_email'] = email.strip()
                            break
                else:
                    print('EMAIL IS AVAILABLE : ', email)
            except:
                traceback.print_exc()

            # DETECT POSTING LANGUAGE OF JOB TITLE AND JOB DESCRIPTION
            try:
                data["title_language"] = self.helper.language_detection(data['job_title'][index], check_title=True)
            except:
                pass
            try:
                data["description_language"] = self.helper.language_detection(data['job_description'][index])
            except:
                pass
            # GET TRANSLATED JOB TITLE
            try:
                if data["title_language"][index] != "en":
                    data["translated_job_title"] = self.helper.translate_text(data["job_title"][index])
                else:
                    data["translated_job_title"] = data["job_title"][index]
            except:
                data["translated_job_title"] = data["job_title"][index]
                pass

            # CREATE COMPANY SLUG
            try:
                company_slug = data["company_name"][index]
                company_slug = company_slug.strip()
                data["company_slug"] = self.helper.other_character_cleaner('-', company_slug)
            except Exception as error:
                print(error)

            # CHECK COMPANY IS AVAILABLE IN THE DATABASE OR NOT
            try:
                data["company_name"] = data["company_name"][index].replace("\\", " ")
                fields = ['id', 'email']
                condition = "name = '%s' OR old_name = '%s'" % (data["company_name"][index].replace("'", "''"), data["company_name"][index].replace("'", "''"))
                response = self.select_data("companies", fields, condition)
                if len(response) == 0:
                    response = self.insert_company_data("companies", data)
                    data["company_id"] = response["id"]
                else:
                    data["company_id"] = response[0]["id"]
                    if data['company_email'][index] != '':
                        company_id = response[0]["id"] if 'id' in response[0] else None
                        company_email = response[0]["email"] if 'email' in response[0] else None
                        if not company_email:
                            print('currently email is not found in the table - Go to update email')
                            update_columns = "%s= '%s'" % ('email', data['company_email'][index])
                            condition = "id = '%s'" % company_id
                            self.update_multiple_records_two('companies', update_columns, condition)
                            print('data updated')
            except Exception as error:
                print(error)

            # CHECK JOB_TITLE IS AVAILABLE IN THE DATABASE OR NOT
            try:
                data["job_title"] = data["job_title"][index].replace("\\", " ")
                condition = "name = '%s'" % data["job_title"][index].replace("'", "''")
                response = self.select_record("job_titles", condition)
                if response is None:
                    response = self.insert_job_title_data("job_titles", data)
                    data["job_title_id"] = response["id"]
                else:
                    data["job_title_id"] = response["id"] if isinstance(response["id"], int) else 0
            except Exception as error:
                print(error)

            # CHECK JOB_TYPE IS AVAILABLE IN THE DATABASE OR NOT
            try:
                job_type = data["job_type"][index].replace(" ", "_").replace("-", "_")
                job_type = job_type.upper()
                condition = "name = '%s'" % job_type
                response = self.select_record("job_types", condition)

                # WHEN CAN'T FIND JOB TYPE, TRY TO GET JOB TYPE FROM JOB TITLE AND JOB DESCRIPTION
                if not response:
                    description = str(data['job_description'][index]) if 'job_description' in data else '' + str(data['job_description_json'][index]) if 'job_description_json' in data else ''
                    job_type = self.helper.job_type_finder("%s %s" % (data["job_title"], description))
                    if job_type:
                        condition = "name = '%s'" % job_type
                        response = self.select_record("job_types", condition)
                data["job_type_id"] = response["id"] if isinstance(response["id"], int) else 0
            except Exception as error:
                print(error)

            # CHECK IS THERE "Working From Home" TEXT WITH CITIES OR DISTRICTS
            try:
                cities = data["location"][index]
                city_list = cities.split(",")
                for city in city_list:
                    city = city.strip()
                    if city == "Working From Home":
                        data["work_place"] = "work_from_home"
            except Exception as error:
                print(error)

            try:
                districts = data["district"][index]
                district_list = districts.split(",")
                for district in district_list:
                    district = district.strip()
                    if district == "Working From Home":
                        data["work_place"] = "work_from_home"
            except Exception as error:
                print(error)

            # CHECK JOB IS ALREADY AVAILABLE IN THE DATABASE OR NOT
            try:
                condition = "job_source = '%s' and unique_key = '%s'" % (data["job_source_name"][index], data["unique_key"][index])
                response = self.select_record("jobs", condition)
                if response is None:
                    try:
                        slug_company_name = str(data["company_name"][index]).strip()
                        slug_company_name = self.helper.other_character_cleaner('-', slug_company_name)
                    except:
                        slug_company_name = ''
                    try:
                        slug_job_title = str(data["translated_job_title"][index]).strip()
                        slug_job_title = self.helper.other_character_cleaner('-', slug_job_title)
                    except:
                        slug_job_title = ''
                    data["slug"] = "%s-%s-%s" % (slug_company_name, slug_job_title, today)
                    response = self.insert_job_data("jobs", data)
                    data["job_id"] = response["id"]
                    print("Data Inserted..... Job ID:", data["job_id"])
                else:
                    return response
            except Exception as error:
                print(error)

            # CHECK CITY_ID IS AVAILABLE IN THE DATABASE OR NOT
            try:
                if data["location"][index] != '':
                    cities = data["location"][index]
                    city_list = cities.split(",")
                    for city in city_list:
                        try:
                            city = city.replace('(', '').replace(')', '').replace('District', '')
                            city = city.strip()
                            fields = ['id', 'district_id']
                            condition = "name_en = '%s' OR name_si = '%s' OR name_ta = '%s'" % (city, city, city)
                            response = self.select_data("cities", fields, condition)
                            if response:
                                data["city_id"] = response[0]["id"] if isinstance(response[0]["id"], int) else 0
                                data["district_id"] = response[0]["district_id"] if isinstance(response[0]["district_id"],
                                                                                               int) else 0
                            if not response:
                                condition = "name_en = '%s' OR name_si = '%s' OR name_ta = '%s'" % (city, city, city)
                                response = self.select_record("districts", condition)
                                data["district_id"] = response["id"] if isinstance(response["id"], int) else 0
                            # FINALLY INSERT CITY ID AND DISTRICT ID TO THE JOB LOCATIONS TABLE
                            data["from_description"] = 0
                            self.insert_job_locations_data("job_locations", data)
                            break
                        except:
                            pass
                elif data["district"][index] != '':
                    # CHECK DISTRICT_ID IS AVAILABLE IN THE DATABASE OR NOT
                    try:
                        districts = data["district"][index]
                        district_list = districts.split(",")
                        for district in district_list:
                            try:
                                district = district.replace('(', '').replace(')', '').replace('District', '')
                                district = district.strip()
                                condition = "name_en = '%s' OR name_si = '%s' OR name_ta = '%s'" % (
                                district, district, district)
                                response = self.select_record("districts", condition)
                                data["district_id"] = response["id"] if isinstance(response["id"], int) else 0
                                data["from_description"] = 0
                                # FINALLY INSERT CITY ID AND DISTRICT ID TO THE JOB LOCATIONS TABLE
                                self.insert_job_locations_data("job_locations", data)
                                break
                            except:
                                pass
                    except Exception as error:
                        print(error)
                else:
                    if data["job_source_name"][index] not in ('Indeed', 'Remoteglobal'):
                        # FIND LOCATION IN JOB DESCRIPTION
                        if 'job_description' in data:
                            job_description = data['job_description'][index]
                            soup = BeautifulSoup(job_description, features="lxml")
                            job_description = (soup.get_text('\n')).replace('\n', ' ')
                        elif 'job_description_json' in data:
                            job_description_json = ast.literal_eval(data['job_description_json'][index])
                            job_description = ''
                            for block_k, block_v in job_description_json.items():
                                for paragraph_list_k, paragraph_list_v in block_v.items():
                                    for paragraph in paragraph_list_v:
                                        job_description += '%s ' % paragraph
                        else:
                            job_description = None

                        if job_description:
                            city_df = pd.read_csv("{}/input/city_df.csv".format(get_base_path()), encoding='latin-1')
                            city_df['name_en'] = city_df['name_en'].str.lower()
                            response_city = self.helper.location_finder(job_description, city_df)
                            if response_city:
                                filtered_city_df = city_df.loc[city_df['name_en'] == response_city]
                                city_id = filtered_city_df['id'].iat[0]
                                district_id = filtered_city_df['district_id'].iat[0]
                                print('CITY FOUND FROM DESCRIPTION - CITY ID:', city_id, ' DISTRICT ID:', district_id)
                                data["city_id"] = city_id
                                data["district_id"] = district_id
                                data["from_description"] = 1
                                self.insert_job_locations_data("job_locations", data)
            except Exception as error:
                print(error)

            # GET MAPPING CATEGORY ID OR IDS AND INSERT THEM TO JOBS_JOB_CATEGORIES PIVOT TABLE
            try:
                category_list = data["category"][index].split(",")
                for category in category_list:
                    try:
                        platform_type = 'App\\\\%s' % data["job_source_name"][index]
                        print('platform_type : ', platform_type)
                        condition = "category_name = '%s' AND platform_type = '%s'" % (category, platform_type)
                        response = self.select_mapping_category_id("job_categories_maps", condition)
                        print('response : ', response)
                        if response:
                            data["pivot_job_id"] = data["job_id"]
                            data["pivot_category_id"] = response["mapping_category_id"]
                            self.insert_jobs_job_categories_data("jobs_job_categories", data)

                            try:
                                print('\n***************************************************************************')
                                print('min_salary : %s, max_salary : %s' % (data['min_salary'][index], data['max_salary'][index]))
                                if data['min_salary'][index] == '' or data['max_salary'][index] == '':
                                    print('GOT TO SALARY MANUAL UPDATE')
                                    self.salary_manual_updater(data["job_id"][index], data["pivot_category_id"][index])
                                else:
                                    print('SALARY WAS ALREADY INSERTED')
                            except:
                                traceback.print_exc()
                            print('***************************************************************************\n')
                        else:
                            self.salary_manual_updater(data["job_id"][index], 0)
                    except:
                        pass
                return None
            except Exception as error:
                print(error)
                return None

    def salary_manual_updater(self, job_id, category_id):
        try:
            if category_id:
                if category_id in (14, 15, 24):
                    min_salary = 50000
                    max_salary = 250000
                else:
                    min_salary = 50000
                    max_salary = 150000
            else:
                min_salary = 50000
                max_salary = 150000

            # JOB TABLE UPDATE
            job_update_columns = "currency = '%s', min_salary = '%s', max_salary = '%s', is_valid_salary = '%s'" % (
            'Rs', min_salary, max_salary, 0)
            job_condition = "id = '%s'" % job_id
            self.update_multiple_records_two('jobs', job_update_columns, job_condition)
            print('Job data updated')
        except:
            pass

    # CHECK COMPANY IS AVAILABLE IN THE DATABASE OR NOT
    def check_company_availability(self, company_name):
        company_name = company_name.replace("'", "''")
        try:
            condition = "name = '%s'" % company_name
            response = self.select_record("companies", condition)
            return response
        except:
            pass

    def check_job_availability(self, job_source_name, unique_key):
        try:
            condition = "job_source = '%s' and unique_key = '%s'" % (job_source_name, unique_key)
            print('condition', condition)
            response = self.select_record("jobs", condition)
            return response
        except:
            pass

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

    def select_mapping_category_id(self, table_name, condition=None):
        record_row = None
        sql = "SELECT `mapping_category_id` FROM " + table_name
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
                "mapping_category_id": result[0]
            }
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

    def insert_company_data(self, table_name, data):
        record_row = None
        for index, row in data.iterrows():
            insert_data = {}
            insert_data['user_id'] = self.check_nun('user_id', row)
            insert_data['industry_id'] = self.check_nun('industry_id', row)
            insert_data['name'] = self.check_nun('company_name', row)
            insert_data['description'] = self.check_nun('company_description', row)
            insert_data['email'] = self.check_nun('company_email', row)
            insert_data['website'] = self.check_nun('company_website', row)
            insert_data['address'] = self.check_nun('company_address', row)
            insert_data['telephone'] = self.check_nun('company_telephone', row)
            insert_data['size'] = self.check_nun('company_size', row)
            insert_data['slug'] = self.check_nun('company_slug', row)
            insert_data['created_at'] = self.check_nun('created_at', row)
            insert_data['updated_at'] = self.check_nun('updated_at', row)
            insert_data['logo_image_path'] = self.check_nun('s3_url_company_logo', row)

            filtered_insert_data = self.pop_null_values(insert_data)

            last_id = self.common_routing_insert_dictionary_data_to_db(table_name=table_name, **filtered_insert_data)
            record_row = {"id": last_id}
        return record_row

    def insert_job_title_data(self, table_name, data):
        record_row = None
        for index, row in data.iterrows():
            insert_data = {}
            insert_data['name'] = self.check_nun('job_title', row)
            insert_data['posting_language'] = self.check_nun('title_language', row)
            insert_data['translated_name'] = self.check_nun('translated_job_title', row)
            insert_data['created_at'] = self.check_nun('created_at', row)
            insert_data['updated_at'] = self.check_nun('updated_at', row)

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
