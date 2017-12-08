# coding:utf-8

# @author:apple
# @date:16/4/29
from web.utils.webclient import WebClient
import time
import json
from datetime import datetime
import logging

url = 'http://api.goseek.cn/Tools/holiday?date=%s'
client = WebClient()

cur_date = {"date": '', 'is_trade': False}


def get_cur_date():
    return time.strftime('%Y%m%d', time.localtime(time.time()))


def is_trade_date():
    if cur_date['date'] != get_cur_date():
        cur_date['date'] = get_cur_date()
        day_of_week = datetime.now().weekday()
        if day_of_week == 0 or day_of_week == 6:
            cur_date['is_trade'] = False
        else:
            data = client.get(url)
            if data.status == 200:
                d = json.loads(data.data)['data']
                cur_date['is_trade'] = d == 0
                pass
            else:
                cur_date['is_trade'] = True
                logging.error("获取节假日数据异常:%s" % data.status)

    return cur_date['is_trade']



