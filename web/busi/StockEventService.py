# coding:utf-8
from web.utils import EmailSend
from web.utils.StockFile import StockFile
from web.utils import TemplateUtils
from web.db.dbexec import DBExec
from web.dataCenter import THSDataCenter
from web.dataCenter import StockData
from web.busi.StockAnalysis import *
from web.utils import Holiday
import logging
from web.db import Query


class StockEventService(object):
    def __init__(self):
        self.thsData = THSDataCenter.THSData()
        self.thsDataOther = THSDataCenter.THSDataOther()
        self.db = DBExec(Query.QUERY_STOCK_EVENT, "")
        pass

    def update_all_stock_event(self):
        """
        更新所有stock事件
        :return:
        """
        stock_list = DBExec(Query.QUERY_STOCK, "FIND_STOCK_ALL").execute(None)
        # stock_list = [{'code':'002606'}]
        result = []
        logging.info("开始获取 stock事件 更新并发处理--->获取stock个数:%s" % (stock_list and len(stock_list) or 0))
        try:
            CommonUtils.start_many_thread(stock_list, handleSize=200, target=self.get_stock_event_batch,
                                          args=(result,), name="stock事件 更新并发处理", asyn=False)
        except Exception, e:
            logging.error("stock事件 更新并发处理--->失败:%s" % e)
        if len(result) > 0:
            logging.info("开始保存stock事件 --->处理个数：%s" % len(result))
            for res in result:
                self.save_stock_event(res)
            logging.info("开始保存stock事件 --->处理完成")
        else:
            logging.info("stock事件 更新并发处理--->未能获取stock事件")

    def save_stock_event(self, result):
        if result is None or len(result) == 0:
            return
        stock_code = result[0]['stock_code']
        # self.db.set(QUERY_PATH, "SAVE_DAILY_STOCK")
        event_list = self.db.setId("GET_STOCK_DAILY_STOCK_FUTURE").execute({'stock_code', stock_code}, print_sql=False)
        # 新增

        # 删除

        # 修改

        self.db.commitTrans()
        pass

    def get_stock_event_batch(self, stock_list, result):
        """
        批量获取 时间
        :param stock_list:
        :param result:
        :return:
        """
        count = 0
        for stock in stock_list:
            res = self.thsDataOther.get_stock_important_event(stock['code'])
            if res:
                count += 1
                result.append(res)
        pass
