import sys
from lists import *

try:
    id = new_list()
    get_list(id)
except KeyError as e:
    print('exception')
    print(e)
    print(sys.exc_info()[0])
