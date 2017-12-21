# coding:utf-8

# @author:apple
# @date:16/3/30
from web import app
from web.views.login import login
from web.views.shares import shares

app.register_blueprint(login)
app.register_blueprint(shares)


