import pytest
from lists import ListApp

# settings
DB_NAME = 'lists'

lists = ListApp('sqlite:///:memory:')
print('got list app in tests', lists)

def test_lists():
  list1 = lists.new()
  assert(type(list1) is dict)

  lists.stop()
