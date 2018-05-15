# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2018/05/15
from web.utils import EmailSend
from web.utils.StockFile import StockFile
from web.utils import TemplateUtils
from web.db.dbexec import DBExec
from web.dataCenter import THSDataCenter
from web.dataCenter import StockData
from web.busi.StockEventService import StockEventService
from web.utils import Holiday
import logging
from web.utils import ConfigUtils

from web.db import Query


class TaskService(object):
    def __init__(self):
        self.db = DBExec(Query.QUERY_FINANCE_TASK, "")
        pass

    def stock_event(self):

        se = StockEventService()
        # 获取未获取的事件的 stock
        stock_list = self.db.setId("GET_TASK_LIST").execute(
            {"busi_type": "stock", "task_1": 2,
             "limit": int(ConfigUtils.get_val('task', 'eventLimit', default_val=25))})
        se.update_all_stock_event(stock_list=stock_list)
        self.db.setId("UPDATE_TASK").execute({"busi_type": "stock", "task_1": 1, "code_list": stock_list})
        return stock_list

    def reset_stock_event(self):
        logging.info("重置任务---stock event 开始")
        # 获取未获取的事件的 stock
        count = self.db.setId("UPDATE_TASK").execute({"busi_type": "stock", "task_1": 2})
        logging.info("重置任务---stock event 完成：%s" % count)


if __name__ == '__main__':
    ts = TaskService()
    print ts.stock_event()
