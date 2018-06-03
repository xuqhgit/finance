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


def get_cur_year():
    return time.strftime('%Y', time.localtime(time.time()))


def get_cur_month():
    return time.strftime('%m', time.localtime(time.time()))


def is_trade_time():
    """
    是否是交易时间 其中已 925 竞价结束为开始时间
    :return:
    """
    s_k = 925
    s_s = 1130
    x_k = 1300
    x_s = 1500
    cur_time = time.strftime('%H%M', time.localtime(time.time()))
    cur_time = int(cur_time)
    if s_k <= cur_time < s_s or x_k <= cur_time < x_s:
        return True
    return False


def is_trade_date_time():
    """
    判断是否是交易日期内的交易时间
    :return:
    """
    return is_trade_date() and is_trade_time()


def is_trade_date():
    if cur_date['date'] != get_cur_date():
        cur_date['date'] = get_cur_date()
        day_of_week = datetime.now().isoweekday()
        if day_of_week > 5:
            cur_date['is_trade'] = False
        else:
            data = client.get(url % cur_date['date'])
            if data.status == 200:
                d = json.loads(data.data)['data']
                cur_date['is_trade'] = d == 0
                pass
            else:
                cur_date['is_trade'] = True
                logging.error("获取节假日数据异常:%s" % data.status)
        logging.info("当前为交易日：%s" % cur_date['is_trade'])
    return cur_date['is_trade']


if __name__ == '__main__':
    print is_trade_date()
