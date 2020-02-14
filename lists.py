import time
from threading import Timer
import lib
import os
from dotenv import load_dotenv
import mysql.connector
import logging

# settings
load_dotenv()
DB_HOST = os.getenv('DB_HOST') or 'localhost'
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

DB_NAME = 'lists'
LIST_TABLE = 'Lists'
ENTRY_TABLE = 'Entries'


def db_connect():
    db = mysql.connector.connect(
      host=DB_HOST,
      user=DB_USER,
      passwd=DB_PASSWORD
    )
    cursor = db.cursor()
    return db, cursor

db, cursor = db_connect()

def execute(*args):
    global db
    global cursor
    try:
        cursor.execute(*args)
    except mysql.connector.DatabaseError as err:
        logging.error('DB ERROR')
        db, cursor = db_connect()
        execute(f'USE {DB_NAME}')
        cursor.execute(*args)


execute(f'CREATE DATABASE IF NOT EXISTS {DB_NAME}')
execute(f'USE {DB_NAME}')
execute(f'''
    CREATE TABLE IF NOT EXISTS {LIST_TABLE} (
        id VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
    )
''')
execute(f'''
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
    execute(f'DELETE FROM {LIST_TABLE} WHERE id = %s', (id,))
    db.commit()

def new():
    list_id = lib.random_string()
    execute(f'INSERT INTO {LIST_TABLE} (id) VALUES (%s)', (list_id,))
    db.commit()

    delete_timer = Timer(LIST_LIFETIME, delete, (list_id,))
    delete_timer.start()

    return list_id

def get(id):
    execute(f'SELECT * FROM {ENTRY_TABLE} WHERE list_id = %s', (id,))
    entries = cursor.fetchall()
    my_list = {}
    my_list['id'] = id
    my_list['items'] = [entry for _, entry, _ in entries]
    return my_list

def add(list_id, item):
    execute(
        f'INSERT INTO {ENTRY_TABLE} (text, list_id) VALUES (%s, %s)', (item, list_id,)
    )
    db.commit()

