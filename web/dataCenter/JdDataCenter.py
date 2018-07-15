# coding:utf-8
import json
import logging
import time

from web.utils import StringUtils
from web.utils.webclient import WebClient
from bs4 import BeautifulSoup


class JdData(object):
    """
    京东数据
    """

    def get_fund_cur_stock(self, code, endDate=None):
        """
        获取基金股票数据
        :param code:
        :param endDate:
        :return:
        数据描述
        [{
        "dayIncress": -0.00139,
        "fundCode": "166005",
        "stockCode": "601166",
        "stockHoldAmount": "377.07",
        "stockMarketValue": 65044575.00,
        "stockName": "兴业银行",
        "stockPeriodDate": "2015-06-30",
        "stockRatio": 5.1000}]
        """
        url = 'http://dp.jr.jd.com/service/getStocksInfo/%s.do?callback=' \
              'jQuery18308871135887562279_%s&_=%s' % (code, int(time.time()), int(time.time()))
        c = WebClient()
        resp = c.get(url)
        result = []
        if resp.status == 200:
            h = resp.data.split("(")[1].replace(")", "")
            print h
            if bool(h) is False:
                logging.error("【jd】获取基金[%s]stock 数据：无数据" % (code))
                return result
            data = json.loads(h)
            if bool(data) is False:
                logging.error("【jd】获取基金[%s]stock 数据：无数据" % (code))
                return result

            for i in range(0, len(data)):
                d = data[i]
                if endDate and d['stockPeriodDate'] != endDate:
                    continue
                stock_code = d['stockCode']
                stock_name = d['stockName']
                scale = float(d['stockRatio'])
                quantity = float(d['stockHoldAmount'])
                mc = float(d['stockMarketValue'])
                result.append({"stock_code": stock_code, "stock_name": stock_name, "mc": mc, "scale": scale,
                               "quantity": quantity, "end_date": endDate, "fund_code": code})

        else:
            logging.error("【jd】获取基金公司[%s]数据异常,请求码:%s" % (code, resp.status))
        return result

if __name__ == '__main__':
    jd = JdData()
    print jd.get_fund_cur_stock("166005")
