import time
from threading import Timer
import lib
import os
from dotenv import load_dotenv
import mysql.connector

# settings
load_dotenv()
DB_HOST = os.getenv('DB_HOST') or 'localhost'
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

DB_NAME = 'lists'
LIST_TABLE = 'Lists'
ENTRY_TABLE = 'Entries'


mydb = mysql.connector.connect(
  host=DB_HOST,
  user=DB_USER,
  passwd=DB_PASSWORD
)
cursor = mydb.cursor()
cursor.execute(f'CREATE DATABASE IF NOT EXISTS {DB_NAME}')
cursor.execute(f'USE {DB_NAME}')
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {LIST_TABLE} (
        id VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
    )
''')
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {ENTRY_TABLE} (
        id INT NOT NULL AUTO_INCREMENT,
        text VARCHAR(255) NOT NULL,
        list_id VARCHAR(255) NOT NULL,
        FOREIGN KEY (list_id) REFERENCES {LIST_TABLE}(id) ON DELETE CASCADE,
        PRIMARY KEY (id)
    )
''')


lists = {}

LIST_LIFETIME = 1.0 * 3600 * 24 # 24 hours



def delete(id):
    cursor.execute(f'DELETE FROM {LIST_TABLE} WHERE id = %s', id)
    mydb.commit()

def new():
    list_id = lib.random_string()
    cursor.execute(f'INSERT INTO {LIST_TABLE} (id) VALUES (%s)', list_id)
    mydb.commit()

    delete_timer = Timer(LIST_LIFETIME, delete, (list_id,))
    delete_timer.start()

    return list_id

def get(id):
    cursor.execute(f'SELECT * FROM {ENTRY_TABLE} WHERE list_id = %s', id)
    entries = cursor.fetchall()
    return entries

def add(id, item):
    cursor.execute(
        f'INSERT INTO {ENTRY_TABLE} (text, list_id) VALUES (%s, %s)', item, id
    )

