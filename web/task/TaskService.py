# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2018/05/15

from web.db.dbexec import DBExec

from web.busi.StockEventService import StockEventService
from web.busi.StockService import StockService
from web.busi.FundService import FundService

import logging
from web.utils import ConfigUtils

from web.db import Query

waiting = 2
handle = 1


class TaskService(object):
    def __init__(self):
        self.db = DBExec(Query.QUERY_FINANCE_TASK, "")
        pass

    def stock_event(self):
        se = StockEventService()
        # 获取未获取的事件的 stock
        stock_list = self.db.setId("GET_TASK_LIST").execute(
            {"busi_type": "stock", "task_1": waiting,
             "limit": int(ConfigUtils.get_val('task', 'eventLimit', default_val=25))})
        if len(stock_list) == 0:
            return stock_list
        se.update_all_stock_event(stock_list=stock_list)
        self.db.setId("UPDATE_TASK").execute({"busi_type": "stock", "task_1": handle, "code_list": stock_list})
        self.db.commitTrans()
        return stock_list

    def reset_stock_event(self):
        logging.info("重置任务---stock event 开始")
        # 获取未获取的事件的 stock
        count = self.db.setId("UPDATE_TASK").execute({"busi_type": "stock", "task_1": 2})
        logging.info("重置任务---stock event 完成：%s" % count)
        self.db.commitTrans()

    def stock_daily(self):
        ss = StockService()
        db = DBExec(Query.QUERY_FINANCE_TASK, "")
        task_name = 'task_2'
        # 获取未获取的事件的 stock
        stock_list = db.setId("GET_TASK_LIST").execute(
            {"busi_type": "stock", task_name: waiting,
             "limit": int(ConfigUtils.get_val('task', 'stockDailyLimit', default_val=100))})
        if len(stock_list) == 0:
            return stock_list
        result = ss.saveAllDailyStocks(stock_list=stock_list, single=True, handleSize=11)
        if bool(result):
            db.setId("UPDATE_TASK").execute({"busi_type": "stock", task_name: handle, "code_list":
                [{'code':result[i]['stock_code']} for i in range(0, len(result))]})
        db.commitTrans()
        return stock_list

    def reset_stock_daily(self):
        logging.info("重置任务---stock daily 开始")
        # 获取未获取的事件的 stock
        db = DBExec(Query.QUERY_FINANCE_TASK, "")
        count = db.setId("UPDATE_TASK").execute({"busi_type": "stock", "task_2": waiting})
        logging.info("重置任务---stock event 完成：%s" % count)
        db.commitTrans()

    def stock_last(self):
        ss = StockService()
        db = DBExec(Query.QUERY_FINANCE_TASK, "")
        task_name = 'task_3'
        # 获取未获取的事件的 stock
        stock_list = db.setId("GET_TASK_LIST").execute(
            {"busi_type": "stock", task_name: waiting,
             "limit": int(ConfigUtils.get_val('task', 'stockLastLimit', default_val=100))})
        if len(stock_list) == 0:
            return stock_list
        result = ss.saveAllDailyStocksLast(stock_list=stock_list, single=True, handleSize=11)
        if bool(result):
            db.setId("UPDATE_TASK").execute({"busi_type": "stock", task_name: handle, "code_list":result})
        db.commitTrans()
        return stock_list

    def reset_stock_last(self):
        logging.info("重置任务---stock event 开始")
        # 获取未获取的事件的 stock
        db = DBExec(Query.QUERY_FINANCE_TASK, "")
        count = db.setId("UPDATE_TASK").execute({"busi_type": "stock", "task_3": waiting})
        db.commitTrans()
        logging.info("重置任务---stock event 完成：%s" % count)

    def fund_stock(self):
        fs = FundService()
        db = DBExec(Query.QUERY_FINANCE_TASK, "")
        task_name = 'task_1'
        func_list = db.setId("GET_TASK_LIST").execute(
            {"busi_type": "fund", task_name: waiting,
             "limit": int(ConfigUtils.get_val('task', 'fundStockSaveLimit', default_val=300))})
        if len(func_list) == 0:
            return func_list
        fs.save_fund_stock(func_list)
        db.setId("UPDATE_TASK").execute({"busi_type": "fund", task_name: handle, "code_list": func_list})
        db.commitTrans()

    def reset_fund_stock(self):
        logging.info("重置任务---fund stock 开始")
        # 获取未获取的事件的 stock
        db = DBExec(Query.QUERY_FINANCE_TASK, "")
        count = db.setId("UPDATE_TASK").execute({"busi_type": "fund", "task_1": waiting, "t_task_1": handle})
        db.commitTrans()
        logging.info("重置任务---fund stock 完成：%s" % count)


if __name__ == '__main__':
    ts = TaskService()
    print ts.fund_stock()
