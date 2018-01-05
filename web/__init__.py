# -*- coding: utf-8 -*-
import logging
import os
import sys

from flask import Flask

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'baidupbgzjx123456'

_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
web_dir = os.path.dirname(__file__)
_log_dir = os.path.join(_dir, 'logs')

if not os.path.isdir(_log_dir):
    os.makedirs(_log_dir)
# 设置默认的level为DEBUG
# 设置log的格式
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(process)s, %(levelname)s: %(message)s",
    # datefmt='%a, %d %b %Y %H:%M:%S',
    filename=_log_dir + '/finance.log',
    filemode='w'
)
#################################################################################################
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

from web import view
from web.task import TaskManage
from web import views

TaskManage.start()
