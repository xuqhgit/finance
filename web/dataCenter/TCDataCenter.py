# coding:utf-8

import logging
import random

from web.utils import StringUtils
from web.utils.webclient import WebClient

# 腾讯当前shares 数据
TX_CUR_DATA_URL = 'http://web.sqt.gtimg.cn/q=%s?r=%s'
client = WebClient()


class TCData(object):
    """
    腾讯财经

    """

    @staticmethod
    def getCurData(code):
        """
        获取实时的股票头部数据
        :param code: 股票代码 格式为:sh+代码
        :return: 获取指定格式的dict数据
        """
        url = TX_CUR_DATA_URL % ((StringUtils.stock_code_type(code) == 'sh' and 'sh' or 'sz') + code, random.random())
        req = client.get(url)
        if req.status == 200:
            splitStr = '="'
            da = len(req.data.split(splitStr, 2)) > 1 and req.data.split(splitStr, 2)[1] or None
            if da is None:
                return None
            da = da[0:len(da) - 1].replace("~~~", "~~").decode("gbk").encode("utf-8")
            strs = da.split('~~', 2)
            b = strs[0].split('~', 7)
            if len(b) < 2:
                logging.error("【tc】获取【%s】数据【%s】错误：%s" % (code, req.data, '数据不完整'))
                return None
            if float(b[3]) == 0 or float(b[5]) == 0:
                return None
            c = b[7].split('~', 34)

            a = strs[1].split('~', 9)
            try:

                result = {'high_end': float(a[6]),  # 涨停
                          'low_end': float(a[7]),  # 跌停
                          'high_price': float(a[0]),  # 最高
                          'low_price': float(a[1]),  # 最低
                          'price': float(b[3]),  # 当前价
                          'open_price': float(b[5]),  # 开盘价
                          'turnover_rate': float(c[31]),  # 换手
                          'close_price': float(b[4]),  # 昨收
                          'growth': float(c[25]),  # 涨幅
                          'amplitude': float(a[2]),  # 振动幅度
                          'volume_transaction': float(b[6]),  # 振动幅度
                          'stock_code': code,
                          'rs': 'tc',
                          'chg': float(c[24])  # 涨跌
                          }
            except Exception, e:
                logging.error("【tc】获取【%s】数据【%s】错误：%s" % (code, req.data, e))
                return None
            return result
        else:
            logging.error("【TC】获取[%s]实时数据出现请求错误,请求码:%s" % (code, req.status))
            return None

if __name__=='__main__':
    print TCData.getCurData('601999')