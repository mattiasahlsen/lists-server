import os
import logging
from flask import Flask, escape, request, jsonify
from dotenv import load_dotenv
from lists import ListApp

DIR = os.path.dirname(os.path.realpath(__file__))

if not os.getenv('FLASK_ENV') == 'development':
    logging.basicConfig(
        filename=DIR + '/error.log',
        level=logging.WARNING,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

app = Flask(__name__)

# settings
load_dotenv()
DB_HOST = os.getenv('DB_HOST') or 'localhost'
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = 'lists'

lists = ListApp(f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
print('got list app', lists)

@app.route('/list/<id>', methods=['GET', 'DELETE'])
def list(id):
    if id is None: return 'No id parameter provided', 400

    if (request.method == 'GET'):
        l = lists.get(id)
        if l: return l
        else: return 'List not found', 404
    elif (request.method == 'DELETE'):
        deleted = lists.delete(id)
        returned = 'List deleted' if deleted else ('List not found', 404)
        return returned
    else:
        raise Exception('Unsupported HTTP method.')

@app.route('/list', methods=['POST'])
def create_list():
    return lists.new()


@app.route('/list/<list_id>/item', methods=['POST'])
def add_item(list_id):
    if list_id is None: return 'No id parameter provided', 400

    if not request.content_type.startswith('application/json'):
        return 'Content-Type must be application/json', 400

    data = request.get_json()
    if not data or not "item" in data:
        return 'Bad format of data, should be { "item": ... }', 400

    print('data', data)
    new_item = data['item']

    # success
    changed_list = lists.add_item(list_id, new_item)
    return changed_list or ('List not found', 404)

@app.route('/item/<item_id>', methods=['DELETE'])
def remove_item(item_id):
    if item_id is None: return 'No id parameter provided', 400

    deleted = lists.delete_item(item_id)
    returned = 'Item deleted' if deleted else ('Item not found', 404)
    return returned
