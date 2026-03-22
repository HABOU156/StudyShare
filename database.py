import os

import pymysql
from dotenv import load_dotenv

from sql_utils import run_sql_file


class Database:
    def __init__(self):
        """
            Chargez les variables d'environnement de votre fichier .env, puis complétez les lignes 15 à 19 afin de récupérer les valeurs de ces variables
        """
        load_dotenv()

        self.host = os.getenv("HOST")
        self.port = int(os.getenv("PORT"))
        self.database = os.getenv("DATABASE")
        self.user = os.getenv("USER")
        self.password = os.getenv("PASSWORD")

        self._open_sql_connection()

    def _open_sql_connection(self):
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database,
            autocommit=True
        )

        self.cursor = self.connection.cursor()

    def get_table_names(self):
        try:
            req = f"SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_type = 'BASE TABLE' AND table_schema = '{self.database}';"
            self.cursor.execute(req)

            res = [x[0] for x in self.cursor.fetchall()]

            return res
        except Exception as e:
            print(f"Error while getting table names: {e}")

    def get_table_column_names(self, table):
        try:
            req = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND TABLE_SCHEMA = '{self.database}' ORDER BY ORDINAL_POSITION;"
            self.cursor.execute(req)

            res = [x[0] for x in self.cursor.fetchall()]

            return res
        except Exception as e:
            print(f"Error while getting column names: {e}")

    def get_table_data(self, table):
        try:
            req = f"SELECT * FROM {table};"
            self.cursor.execute(req)

            return [list(x) for x in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error while getting table data: {e}")

    def get_table_primary_key(self, table):
        try:
            req = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table}' AND CONSTRAINT_NAME = 'PRIMARY';"
            self.cursor.execute(req)

            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error while getting primary key: {e}")

    def get_table_foreign_keys(self, table):
        try:
            req = f"SELECT COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table}' AND CONSTRAINT_NAME != 'PRIMARY';"
            self.cursor.execute(req)

            foreign_keys = []
            for foreign_key in self.cursor.fetchall():
                foreign_keys.append({
                    "column_name": foreign_key[0],
                    "referenced_table_name": foreign_key[1],
                    "referenced_column_name": foreign_key[2]
                })

            return foreign_keys
        except Exception as e:
            print(f"Error while getting foreign keys: {e}")

    def get_cursor(self):
        return self.cursor

    def get_connection(self):
        return self.connection
