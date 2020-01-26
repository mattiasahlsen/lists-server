import time
from threading import Timer
import lib

lists = {}

LIST_LIFETIME = 1.0 * 3600 * 24 # 24 hours

def delete(id):
    lists.pop(id, None)

def new():
    list_id = lib.random_string()
    lists[list_id] = {
      'id': list_id,
      'items': [],
      'expires': time.time() + LIST_LIFETIME * 1000 # ms
    }

    delete_timer = Timer(LIST_LIFETIME, delete, (list_id,))
    delete_timer.start()

    return list_id

def get(id):
    return lists[id]

def add(id, item):
    lists[id]['items'].append(item)

