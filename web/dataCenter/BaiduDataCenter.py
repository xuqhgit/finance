# coding:utf-8

import json
import logging
import time

from web.utils.webclient import WebClient




class BaiduData(object):
    """
    百度
    """

    @staticmethod
    def getCurData(codes):
        """

        :param codes:列表
        :return:
        """
        client = WebClient()
        url = 'https://gupiao.baidu.com/api/rails/stockbasicbatch?from=pc&os_ver=1&cuid=xxx&vv=100' \
              '&format=json&stock_code=%s&timestamp=%s'
        codes_c = []
        for c in codes:
            codes_c.append('%s%s' % (BaiduData.__stock_code_type(c), c))
        resp = client.get(url % (','.join(codes_c), int(time.time())))
        if resp.status == 200:
            da = resp.data.decode("gbk").encode("utf-8")
            data = json.loads(da)['data']
            result = []
            for i in range(0, len(data)):
                d = data[i]
                res = {
                    'high_price': round(d['high'], 3),  # 最高
                    'low_price': round(d['low'], 3),  # 最低
                    'price': round(d['close'], 3),  # 当前价
                    'open_price': round(d['open'], 3),  # 开盘价
                    'turnover_rate': round(d['turnoverRatio'], 3),  # 换手
                    'close_price': round(d['preClose'], 3),  # 昨收
                    'growth': round(d['netChangeRatio'], 3),  # 涨幅
                    'amplitude': round(d['amplitudeRatio'], 3),  # 振动幅度
                    'volume_transaction': d['volume'],  # 成交量
                    'stock_code': d['stockCode'],
                    'chg': round(d['netChange'], 3),
                    'rs': 'baidu'
                }
                result.append(res)
            return result

        else:
            logging.error("【baidu】获取[%s]实时数据出现请求错误,请求码:%s" % (codes, resp.status))
            return None

    @staticmethod
    def __stock_code_type(code):
        """
        根据stock代码 获取stock类型 s  sz
        :param code:
        :return:
        """
        code_type = 'sh'
        if code[0] == '6':
            code_type = 'sh'
        elif code[0] == '0':
            code_type = 'sz'
        elif code[0] == '3':
            code_type = 'sz'
        return code_type


if __name__ == '__main__':
    sj = BaiduData()
    print sj.getCurData(['603300'])
