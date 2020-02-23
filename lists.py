import threading
import time
from datetime import datetime
from threading import Timer, Thread, Event
import lib
import os
import logging
from dotenv import load_dotenv

import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.mysql import MEDIUMTEXT

# settings
load_dotenv()
DB_HOST = os.getenv('DB_HOST') or 'localhost'
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

DB_NAME = 'lists'
LIST_TABLE = 'List'
ENTRY_TABLE = 'Entry'

LIST_LIFETIME = 1.0 * 3600 * 24 # 24 hours

engine = db.create_engine(f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
Base = declarative_base()

class List(Base):
    __tablename__ = LIST_TABLE
    id = Column(String(255), primary_key=True)
    dies = Column(DateTime)
class Entry(Base):
    __tablename__ = ENTRY_TABLE
    id = Column(Integer, primary_key=True)
    text = Column(MEDIUMTEXT, nullable=False)
    list_id = Column(
        String(255),
        ForeignKey(List.id, ondelete='cascade'),
        nullable=False
    )

List.entries = relationship(Entry, cascade='all, delete-orphan')

Base.metadata.create_all(engine)
Session = sessionmaker(bind = engine)
session = Session()




def alive():
    return datetime.now() < List.dies
def dead():
    return datetime.now() >= List.dies


# cleanup feature
def clean_up():
    session.query(List).filter(dead()).delete()
    session.commit()


class CleanupThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(3600): # every hour
            clean_up()

stopFlag = Event()
thread = CleanupThread(stopFlag)
thread.start()
# stopFlag.set() # stops the thread

def delete(id):
    # returns true if delete is successful
    deleted = session.query(List).filter(List.id == id).delete() == 1
    session.commit()
    return deleted

def new():
    list_id = lib.random_string()
    new_list = List(
        id=list_id,
        dies=datetime.fromtimestamp(time.time() + 24 * 3600) # 24 hour lifetime
    )
    session.add(new_list)
    session.commit()

    return list_id

def get(id):
    l = session.query(List).filter(alive()).first()
    if l == None: return None

    my_list = {}
    my_list['id'] = l.id
    my_list['items'] = [entry.text for entry in l.entries]
    return my_list

def add(list_id, item):
    entry = Entry(text=item, list_id = list_id)
    session.add(entry)
    session.commit()
    return get(list_id)
    

