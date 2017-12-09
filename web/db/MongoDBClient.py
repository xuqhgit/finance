# -*- coding: utf-8 -*-
# author: apple
# createTime: 2016/10/13

from pymongo import MongoClient
from web.utils import ConfigUtils

config = {
    'host': ConfigUtils.get("mongo", "host"),
    'port': int(ConfigUtils.get("mongo", "port")),
    'user': ConfigUtils.get("mongo", "name"),
    'pwd': ConfigUtils.get("mongo", "password")
}
client = MongoClient(config['host'], config['port'])
db = client.finance
db.authenticate(config["user"], config["pwd"])

"""
对于mongo 为了不重复插入数据 采用自定义_id处理
"""


def get_client(collection='def'):
    """
    获取collection client
    :param collection:
    :return:
    """
    return db[collection]


def insert_val(id, val, collection):
    """
    向mongo插入数据
    :param id:
    :param val:
    :param collection:
    :return:
    """
    db[collection].insert({'_id': id, 'value': val})


def insert_json(id, json, collection):
    """
    插入json格式数据
    :param id:
    :param json:
    :param collection:
    :return:
    """
    json['_id'] = id
    db[collection].insert(json)


if __name__ == '__main__':
    print get_client('THS_LAST_MIN').find({'code': '603999'}).count()
