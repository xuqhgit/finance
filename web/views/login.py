# coding:utf-8

# @author:apple
# @date:16/3/30

from flask import Blueprint, render_template, redirect, request, session
from web.utils.webclient import WebClient
import json


login = Blueprint('login', __name__,
                  template_folder='templates',
                  static_folder='static', url_prefix='/login')

