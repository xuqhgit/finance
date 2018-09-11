# coding:utf-8

import json
import logging
import re
import time

from web.utils.webclient import WebClient


regex = r'price_A1\':\[(?P<d1>.*?)\],\'price_A2\':\[(?P<d>.*?)\]'


class SohuData(object):
    """
    搜狐
    """

    @staticmethod
    def getCurData(code):
        """

        :param code:列表
        :return:
        """
        client = WebClient()
        url = 'http://hq.stock.sohu.com/cn/%s/cn_%s-1.html?_=%s'

        resp = client.get(url % (code[3:], code, int(time.time())))
        if resp.status == 200:
            da = resp.data.split("(", 2)[1].decode("gbk").encode("utf-8")
            data = da[0:len(da) - 2]
            p = re.compile(regex)
            m = p.search(data, re.S)
            if bool(m) is False:
                return None
            d = json.loads(str('[%s]' % m.groupdict()['d']).replace("'", '"'))
            d1 = json.loads(str('[%s]' % m.groupdict()['d1']).replace("'", '"'))
            res = {'high_end': float(d[9]),  # 涨停
                   'low_end': float(d[11]),  # 跌停
                   'high_price': float(d[5]),  # 最高
                   'low_price': float(d[7]),  # 最低
                   'price': float(d1[2]),  # 当前价
                   'open_price': float(d[3]),  # 开盘价
                   'average_price': float(d[0]),  # 均价
                   'turnover_rate': float(d[6].replace("%", '')),  # 换手
                   'close_price': float(d[1]),  # 昨收
                   'growth': float(d1[4].replace("%", '')),  # 涨幅
                   'amplitude': float(d[14].replace("%", '')),  # 振动幅度
                   'volume_transaction': int(d[8]),  # 成交量
                   'turnover': int(d[12]),  # 成交额
                   'stock_code': code,
                   'rs': 'sohu',
                   'chg': float(d1[3])  # 涨跌
                   }
            return res

        else:
            logging.error("【Sohu】获取[%s]实时数据出现请求错误,请求码:%s" % (code, resp.status))
            return None


if __name__ == '__main__':
    hx = SohuData()
    print hx.getCurData('603300')
