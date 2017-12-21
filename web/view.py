# coding=utf-8
import time

from web import app
from flask import render_template, request
from web.busi.shares import Shares
from ui import json_view

from web.db.RedisClient import RedisClient


@app.errorhandler(403)
def internal_error(error):
    return render_template('html/403.html'), 403


@app.errorhandler(404)
def internal_error(error):
    return render_template('html/404.html'), 404


@app.errorhandler(405)
def internal_error(error):
    return render_template('html/405.html'), 405


@app.errorhandler(500)
def internal_error(error):
    return render_template('html/500.html'), 500


@app.route('/')
@app.route('/index', methods=['get', 'post'])
def index():
    share = Shares()

    # share.getMinData('20160216', '深市(A)', 'sza')

    return render_template('html/index.html', name='a')


@app.route('/graph', methods=['get', 'post'])
def graph():
    return render_template('html/busi/graph/index.html', name='hope')

@app.route('/to', methods=['get', 'post'])
def to():
    args = request.args
    if request.method == 'POST':
        args = request.form
    p = args["p"]
    return render_template('html/'+p+'.html', name='hope')

@app.route('/loc', methods=['get', 'post'])
def loc():
    return render_template('html/loc.html', name='a')

import json
import time
@app.route('/sendLoc', methods=['get', 'post'])
@json_view
def sendLoc():
    args = request.args
    if request.method == 'POST':
        args = request.form
    name = args["name"]
    de = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    params = {"latitude": args['latitude'], "altitudeAccuracy ": args['altitudeAccuracy'],
              "altitude ": args['altitude'], "speed ": args['speed'], "longitude ": args['longitude'],
              "accuracy": args['accuracy'],"date":de}
    client = RedisClient.get_client()
    client.sadd(name,json.dumps(params))
    return "{'result':'0'}"

