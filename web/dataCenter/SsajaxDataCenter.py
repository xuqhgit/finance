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
                'high_price': round(d['high'],3),  # 最高
                'low_price': round(d['low'],3),  # 最低
                'price': round(d['close'],3),  # 当前价
                'open_price': round(d['open'],3),  # 开盘价
                'turnover_rate': round(d['change'],3),  # 换手
                'close_price': round(d['preclose'],3),  # 昨收
                'growth': round(d['updownper'],3),  # 涨幅
                'amplitude': round(d['swing'],3),  # 振动幅度
                'volume_transaction': round(d['volume'],3),  # 成交量
                'turnover': round(d['value'],3),  # 成交额
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
