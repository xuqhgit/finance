# coding:utf-8

import json
import logging
import time

from web.utils.webclient import WebClient

client = WebClient()

class SsajaxData(object):
    """
    证券之星
    """
    @staticmethod
    def getCurData(code):
        """

        :param code:列表
        :return:
        """
        url = 'http://q.ssajax.cn/webhandler/quote_stock.ashx?fn=jQuery1610&debug=1&code=%s&type=1&_=%s'
        resp = client.get(url % (code, int(time.time())))
        if resp.status == 200:
            da = resp.data.split("(", 2)[1].decode("gbk").encode("utf-8")
            data = json.loads(da[0:len(da) - 2])
            print data
            d = data[0]
            res = {
                'high_price': d['high'],  # 最高
                'low_price': d['low'],  # 最低
                'price': d['close'],  # 当前价
                'open_price': d['open'],  # 开盘价
                'turnover_rate': d['change'],  # 换手
                'close_price': d['preclose'],  # 昨收
                'growth': d['updownper'],  # 涨幅
                'amplitude': d['swing'],  # 振动幅度
                'volume_transaction': d['volume'],  # 成交量
                'turnover': d['value'],  # 成交额
                'stock_code': code,
                'chg': d['updown'],
                'rs': 'Ssajax'
            }
            return res

        else:
            logging.error("【Ssajax】获取[%s]实时数据出现请求错误,请求码:%s" % (code, resp.status))
            return None


if __name__ == '__main__':
    sj = SsajaxData()
    print sj.getCurData('603300')
