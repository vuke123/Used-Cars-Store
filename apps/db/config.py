import psycopg2
import csv
import os
from apps.core.logger import Logger
import json
import pandas as pd

class DatabaseOperation:

    def __init__(self, run_id, data_path, mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'DatabaseOperation', mode)
        self.column_names = {'Year': "FLOAT", 'Mileage': "INTEGER", 'Engine':  "FLOAT", 'Power':  "FLOAT", 'Price': "FLOAT", 'Brand': "INTEGER", 'Normalized_Kilometers':  "FLOAT",
                         'Fuel_Type_CNG': "VARCHAR", 'Fuel_Type_Diesel': "VARCHAR", 'Fuel_Type_LPG': "VARCHAR", 'Fuel_Type_Petrol': "VARCHAR",
                             'Transmission_Automatic': "VARCHAR", 'Transmission_Manual': "VARCHAR"}

        self.database = ""
        self.password = ""
        self.host = ""
        self.user = ""
        self.azure_config_path = "apps/db/azure_config.json"

        try:
            azure_path = os.path.join(os.getcwd(), self.azure_config_path)
            with open(azure_path, 'r') as file:
                azure_config = json.load(file)
                self.database = azure_config["database"]
                self.user = azure_config["user"]
                self.host = azure_config["host"]
                self.password = azure_config["password"]
        except FileNotFoundError:
            print("Error: azure_config.json file not found.")
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON data from azure_config.json.")
        except KeyError as e:
            print(f"Error: Key '{e.args[0]}' not found in azure_config.json.")

    def database_connection(self, database_name):
        try:
            conn = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port="5432"
            )
            self.logger.info("Opened %s database successfully" % database_name)
        except Exception as e:
            self.logger.exception("Error while connecting to database: %s" % e)
            raise ConnectionError
        return conn

    def create_table(self, database_name, table_name):
        try:
            self.logger.info('Start of creating table...')
            conn = self.database_connection(database_name)
            c = conn.cursor()

            if database_name == 'used_cars':
                c.execute("DROP TABLE IF EXISTS " + table_name)

            c.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s",
                (table_name,))
            if c.fetchone()[0] == 1:
                c.close()
                self.logger.info('Tables created successfully')
                self.logger.info("Closed %s database successfully" % database_name)
            else:
                c.execute(f'CREATE TABLE {table_name} (ID serial PRIMARY KEY'');')
                conn.commit()
                for key, type_of_column in self.column_names.items():
                    try:
                        c.execute(f'ALTER TABLE {table_name} ADD COLUMN {key} {type_of_column}')
                        self.logger.info(f'ALTER TABLE {table_name} ADD COLUMN {key}')

                    except Exception as e:
                        self.logger.exception(f'Exception while adding columns {key} is {e}.')
                conn.commit()
                conn.close()
            self.logger.info('End of creating table...')
        except Exception as e:
            self.logger.exception('Exception raised while creating table: %s' % e)
            raise e

    def insert_data(self, database_name, table_name, df):
        conn = self.database_connection(database_name)
        c = conn.cursor()
        self.logger.info('Start of inserting data into table...')
        try:
            for index, row in df.iterrows():
                placeholders = ', '.join(['%s'] * len(row))
                insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({placeholders})"

                c.execute(insert_query, tuple(row))
                conn.commit()

            self.logger.info('Data insertion completed successfully.')
        except Exception as e:
            conn.rollback()
            print(e)
            self.logger.exception('Exception raised while inserting data into table: %s ' % e)
        finally:
            c.close()
            conn.close()
            self.logger.info('End of inserting data into table...')

    def export_csv(self, database_name, table_name):
        self.file_from_db = self.data_path + str('_validation/')
        self.file_name = f'Processed_{table_name}.csv'
        try:
            self.logger.info('Start of Exporting Data into CSV...')
            conn = self.database_connection(database_name)
            sql_select = "SELECT * FROM " + table_name
            cursor = conn.cursor()
            cursor.execute(sql_select)
            results = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
            if not os.path.isdir(self.file_from_db):
                os.makedirs(self.file_from_db)
            csv_file = csv.writer(open(os.path.join(self.file_from_db, self.file_name), 'w', newline=''), delimiter=',',
                                  lineterminator='\r\n', quoting=csv.QUOTE_ALL, escapechar='\\')
            csv_file.writerow(headers)
            csv_file.writerows(results)
            self.logger.info('End of exporting data into CSV...')
        except Exception as e:
            self.logger.exception('Exception raised while exporting data into CSV: %s ' % e)

    def fetch_data_to_dataframe(self, database, table):
        try:
            conn = self.database_connection(database)

            query = f"SELECT * FROM {table}"

            df = pd.read_sql(query, conn)

            df['fuel_type_cng'] = df['fuel_type_cng'].astype(float).astype(int)
            df['fuel_type_lpg'] = df['fuel_type_lpg'].astype(float).astype(int)
            df['fuel_type_petrol'] = df['fuel_type_petrol'].astype(float).astype(int)
            df['fuel_type_diesel'] = df['fuel_type_diesel'].astype(float).astype(int)
            df['transmission_manual'] = df['transmission_manual'].astype(float).astype(int)
            df['transmission_automatic'] = df['transmission_automatic'].astype(float).astype(int)

            conn.close()

            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None