import os
import logging
from flask import Flask, escape, request, jsonify
import lists

DIR = os.path.dirname(os.path.realpath(__file__))


if not os.getenv('FLASK_ENV') == 'development':
    logging.basicConfig(
        filename=DIR + '/error.log',
        level=logging.WARNING,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

app = Flask(__name__)


@app.route('/list')
def get_list():
    id = request.args.get('id')
    if id is None: return 'No id parameter provided', 400

    l = lists.get(id)
    if l: return l
    else: return 'List not found', 404

@app.route('/new-list')
def new_list():
    id = lists.new()
    return id

@app.route('/item', methods=['POST'])
def add_item():
    list_id = request.args.get('id')
    if list_id is None: return 'No id parameter provided', 400

    new_item = request.form['item']

    # success
    changed_list = lists.add(list_id, new_item)
    print(changed_list)
    return changed_list or ('List not found', 404)

@app.route('/delete')
def delete_list():
    id = request.args.get('id')
    if id is None: return 'No id parameter provided', 400

    deleted = lists.delete(id)
    returned = 'List deleted' if deleted else ('List not found', 404)
    return returned

