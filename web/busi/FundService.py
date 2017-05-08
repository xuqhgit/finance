# coding:utf-8

from web.busi import shares
from web.utils.ExcelUtils import ExcelUtils
from web.utils.FileUtils import FileUtils
from web.db.dbexec import DBExec
from web.db.RedisClient import RedisClient
from web.utils.webclient import WebClient
from web.dataCenter import THSDataCenter
import thread
from threading import Thread
import json
import time
import logging

QUERY_PATH = 'query/FUND.xml'


class FundService(object):
    def __init__(self):
        pass

    def saveAllDailyFund(self):
        """
        保存daily fund 数据
        :return:
        """

        db = DBExec(QUERY_PATH, "FIND_FUND_ALL")
        stock_list = db.execute(None)
        size = len(stock_list)
        result = []

        list_len = 100
        if size > 5000:
            list_len = 300
        count = size / list_len + (size % list_len == 0 and 0 or 1)
        thread_list = []
        logging.info("[saveAllDailyFund]开启线程数:%s" % count)
        for i in range(0, count):
            if i == count - 1:
                t = Thread(target=self.getAllDailyFund, args=(stock_list[i * list_len:], result))
                t.start()
            else:
                t = Thread(target=self.getAllDailyFund,
                           args=(stock_list[(i * list_len):((i + 1) * list_len)], result))
                t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        logging.info("[saveAllDailyFund]线程数 %s 执行完成" % count)
        db.set(QUERY_PATH, "SAVE_DAILY_BOND")
        logging.info("[saveAllDailyFund]应插入数据:%s条" % size)
        db_result = db.execute(result)
        logging.info("[saveAllDailyFund]插入数据:%s条" % db_result)
        db.commitTrans()
        return db_result

    def getAllDailyFund(self, list, result):
        center = THSDataCenter.THSData()
        r = []
        cur_date = time.strftime('%Y%m%d', time.localtime(time.time()))
        for s in list:
            code = s['code']
            d = center.getStockPlateInfoByCode(code)
            if d:
                d['trade_date'] = cur_date
                r.append(d)
        result.extend(r)
        pass

    def saveAllDailyFundLast(self):
        """
        保存所有股票当日数据 包含资金等
        :return:
        """
        db = DBExec(QUERY_PATH, "FIND_FUND_ALL")
        stock_list = db.execute(None)
        size = len(stock_list)
        list_len = 100
        if size > 5000:
            list_len = 300
        count = size / list_len + (size % list_len == 0 and 0 or 1)
        thread_list = []
        logging.info("[saveAllDailyFundLast]下载FUND_LAST开启线程数:%s" % count)
        for i in range(0, count):
            if i == count - 1:
                t = Thread(target=self.saveDailyStocksLast, args=(stock_list[i * list_len:], None))
                t.start()
            else:
                t = Thread(target=self.saveDailyStocksLast,
                           args=(stock_list[(i * list_len):((i + 1) * list_len)], None))
                t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        logging.info("[saveAllDailyFundLast]下载FUND_LAST数据完成")
        pass

    def saveDailyStocksLast(self, list, result):
        """
        保存最新股票交易数据到redis中 还有 资金数据
        :param list:
        :return:
        """
        center = THSDataCenter.THSData()
        client = RedisClient().get_client()
        key = THSDataCenter.KEY_STOCK_LAST
        key_m = THSDataCenter.KEY_STOCK_MONEY_LAST
        for s in list:
            code = s['code']
            d = center.getStockLast(code)
            if d:
                h_code = 'hs_%s' % code
                last_date = d[h_code]['date']
                data_str = d[h_code]['data']
                key_temp = key % (last_date[0:4], last_date[4:6], last_date[6:], code)
                client.set(key_temp, data_str)
                d = center.getStockMoneyLast(code)
                if d:
                    data_str = d[h_code]['data']
                    key_m_temp = key_m % (last_date[0:4], last_date[4:6], last_date[6:], code)
                    client.set(key_m_temp, data_str)
        pass


if __name__ == '__main__':
    client = RedisClient().get_client()
    # StockService().saveAllDailyStocksLast()
    # StockService().saveDailyStocksLast([{'code': '603999'}])
    print client.get('THS:2016:09:30:LAST:002810')
    print client.get('THS:2016:09:30:LAST:300511')
    pass
