# coding:utf-8

# @author:apple
# @date:16/4/3
from jinja2 import FileSystemLoader
import os
import logging
from jinja2.environment import Environment
from web.dataCenter import THSDataCenter

import web


env = Environment()
env.loader = FileSystemLoader(web.web_dir + '/templates')
_dir = os.path.dirname(__file__)
loader = FileSystemLoader(_dir)


def get_email(file_name, data):
    try:
        t = env.get_template("email/%s.tmpl" % file_name)
        return t.render(data=data)
    except BaseException, e:
        logging.error("获取email template 错误:%s" % e)


if __name__ == '__main__':
    center = THSDataCenter.THSData()
    print get_email("new_stock", [center.getStockPlateInfoByCode("002919")])
    # import EmailSend
    # EmailSend.send(get_email("new_stock", [center.getStockPlateInfoByCode("002606")]), subtype='html')
