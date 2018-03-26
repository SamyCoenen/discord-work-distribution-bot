#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A discord bot which listens on different channels for incoming requests.
"""
__author__ = "Samy Coenen"
__email__ = "contact@samycoenen.be"
__status__ = "Development"
from flask import Flask, request, abort, Response
from flask_restful import Resource, Api
from functools import wraps
import os
import sys
import string
import random
import urllib.request
import urllib.parse
import json
import datetime
from dateutil.parser import parse
import csv
from flaskext.mysql import MySQL
import time    

app = Flask(__name__)
mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'th6k5gfdkgf54'
app.config['MYSQL_DATABASE_DB'] = 'inventory'
app.config['MYSQL_DATABASE_HOST'] = 'db_inventory'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_CHARSET'] = 'latin1'
mysql.init_app(app)
api = Api(app)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'power' and password == 'mememepowerbot'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/update_metric', methods=["POST"])
def update_active_account():
    if not request.json:
        abort(400)
    data = request.json
    print("received json", file=sys.stderr)
    conn = None 
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("""UPDATE servers SET items=%s WHERE ip=%s AND port=%s""",(data['items'], data['ip'], data['port']))
        conn.commit()
    except Exception as e:
        print(repr(e), file=sys.stderr)
        return Response(
            'Our database is not available at this time.', 503, mimetype='application/json')
    finally:
        if not cursor ==  None:
            cursor.close() 
        if not conn ==  None:
            conn.close()
    return json.dumps(True)

if __name__ == '__main__':
     app.run(host='0.0.0.0')
