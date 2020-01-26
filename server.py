import os
import logging
from flask import Flask, escape, request, jsonify
import lists

app = Flask(__name__)


@app.route('/list', )
def get_list():
    id = request.args.get('id')
    if id is None: return 'No id parameter provided', 400

    return lists.get(id)

    return data

@app.route('/new-list')
def new_list():
    id = lists.new()
    return id

@app.route('/item', methods=['POST'])
def add_item():
    list_id = request.args.get('id')
    if list_id is None: return 'No id parameter provided', 400

    new_item = request.form['item']
    lists.add(list_id, new_item)

    return lists.get(list_id)

@app.route('/delete')
def delete_list():
    id = request.args.get('id')
    if id is None: return 'No id parameter provided', 400

    lists.delete(id)
    return 'List deleted if existed.'


@app.errorhandler(KeyError)
def handle_keyerror(e):
    return 'List not found.', 404

if not os.environ['FLASK_ENV'] == 'development':
    logging.basicConfig(filename='error.log',level=logging.WARNING)
