# coding:utf-8

import json
import logging
import time

from web.utils import StringUtils
from web.utils.webclient import WebClient

client = WebClient()


class EastmoneyData(object):
    """
    东方财富
    """

    @staticmethod
    def getCurData(code):
        """

        :param code:
        :return:
        """
        url = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id=%s%s&token=4f1862fc3b5e77c150a2b985b12db0fd&cb=jQuery183&_=%s'
        resp = client.get(url % (code, StringUtils.stock_code_type_int(code), int(time.time())))
        if resp.status == 200:
            da = resp.data.split("(", 2)[1]
            data = json.loads(da[0:len(da) - 1])
            d = data['Value']
            res = {
                'high_end': float(d[23]),  # 涨停
                'low_end': float(d[24]),  # 跌停
                'high_price': float(d[30]),  # 最高
                'low_price': float(d[32]),  # 最低
                'price': float(d[25]),  # 当前价
                'open_price': float(d[28]),  # 开盘价
                'average_price': float(d[26]),  # 均价
                'turnover_rate': float(d[37]),  # 换手
                'close_price': float(d[34]),  # 昨收
                'growth': float(d[29]),  # 涨幅
                'amplitude': float(d[50]),  # 振动幅度
                'volume_transaction': float(d[31]),  # 成交量
                'turnover': float(d[35].replace('万', '')),  # 成交额
                'stock_code': d[1],
                'chg': d[27],
                'rs': 'eastmoney'

            }
            return res
        else:
            logging.error("【eastmoney】获取[%s]实时数据出现请求错误,请求码:%s" % (code, resp.status))
        return None


if __name__ == '__main__':
    em = EastmoneyData()
    print em.getCurData('603300')
