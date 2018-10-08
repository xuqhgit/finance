# coding:utf-8


from web.db.dbexec import DBExec
from web.db import Query
from web.utils.webclient import WebClient
from web.utils import Holiday

import thread
from threading import Thread
import json
import time
import logging

FUND_DICT = {"end_date": None}


class DictService(object):
    def __init__(self):
        pass

    def get_dict_by_dict_status(self, **params):
        """
        保存所有基金公司信息
        :return:
        """
        return DBExec(Query.QUERY_SYS_DICT, "GET_DICT_BY_DICT_STATUS_SINGLE").execute(params)

    def get_fund_end_date(self):
        """
        獲取當前基金的截止時間
        :return:
        """
        if FUND_DICT['end_date'] == None:
            d = DictService().get_dict_by_dict_status(dict_type="FUND_DATE")
            print d
            FUND_DICT['end_date'] = "%s-%s" % (Holiday.get_cur_year(), d['dict_text'])
        return FUND_DICT['end_date']


if __name__ == '__main__':
    print DictService().get_dict_by_dict_status(dict_type='FUND_DATE')
