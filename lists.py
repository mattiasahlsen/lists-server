import threading
import time
from datetime import datetime
from threading import Timer, Thread, Event
import lib
import os
import logging

import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

LIST_TABLE = 'List'
ENTRY_TABLE = 'Entry'

LIST_LIFETIME = 3600 * 24 # 24 hours

Base = declarative_base()

class List(Base):
    __tablename__ = LIST_TABLE
    id = Column(String(255), primary_key=True)
    expires = Column(DateTime)
    def to_dict(self):
        return {
            'id': self.id,
            'expires': self.expires.timestamp(),
            'items': [entry.to_dict() for entry in self.entries] #[entry.text for entry in self.entries]
        }

class Entry(Base):
    __tablename__ = ENTRY_TABLE
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    list_id = Column(
        String(255),
        ForeignKey(List.id, ondelete='cascade'),
        nullable=False
    )
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text
        }

List.entries = relationship(Entry, cascade='all, delete-orphan')

def alive():
    return datetime.now() < List.expires
def dead():
    return datetime.now() >= List.expires


class CleanupThread(Thread):
    def __init__(self, session, event):
        Thread.__init__(self)
        self.stopped = event
        self.session = session

    def run(self):
        while not self.stopped.wait(3600): # every hour
            self.session.query(List).filter(dead()).delete()
            self.session.commit()


class ListApp:
    def __init__(self, connection):
        engine = db.create_engine(connection)
        self.engine = engine

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind = engine)
        self.session = Session()

        self.stopFlag = Event()
        thread = CleanupThread(self.session, self.stopFlag)
        thread.start()
        # stopFlag.set() # stops the thread

    def stop(self):
        self.engine.dispose()
        self.stopFlag.set()

    def delete(self, id):
        # returns true if delete is successful
        deleted = self.session.query(List).filter(List.id == id).delete() == 1
        self.session.commit()
        return deleted

    def new(self):
        list_id = lib.random_string()
        new_list = List(
            id=list_id,
            expires=datetime.fromtimestamp(time.time() + LIST_LIFETIME)
        )
        self.session.add(new_list)
        self.session.commit()

        print(new_list.to_dict())
        return new_list.to_dict()

    def get(self, id):
        l = self.session.query(List).filter(alive()).filter(List.id == id).first()
        if l == None: return None

        return l.to_dict()

    def add_item(self, list_id, item):
        entry = Entry(text=item, list_id = list_id)
        self.session.add(entry)
        self.session.commit()
        return self.get(list_id)

    def delete_item(self, item_id):
        deleted = self.session.query(Entry).filter(Entry.id == item_id).delete() == 1
        self.session.commit()
        return deleted

