# coding:utf-8

import json
import logging
import random

from web.utils.webclient import WebClient



class JRJData(object):
    """
    金融街
    """

    @staticmethod
    def getCurData(codes):
        """

        :param codes:列表
        :return:
        """
        client = WebClient()
        url = 'http://q.jrjimg.cn/?q=cn|s&i=%s&n=mainQuote&c=l&_=%s'
        resp = client.get(url % (",".join(codes), random.random()))
        if resp.status == 200:

            da = resp.data.split("=", 2)[1].decode("gbk").encode("utf-8")
            sda = da.split('HqData:')[1]
            data = json.loads(sda[0:len(sda) - 3])
            result = []
            for i in range(0, len(data)):
                d = data[i]
                res = {
                    'high_end': float(d[3]),  # 涨停
                    'low_end': float(d[4]),  # 跌停
                    'high_price': float(d[9]),  # 最高
                    'low_price': float(d[10]),  # 最低
                    'price': float(d[11]),  # 当前价
                    'open_price': float(d[8]),  # 开盘价
                    'average_price': float(d[7]),  # 均价
                    'turnover_rate': float(d[24]),  # 换手
                    'close_price': float(d[5]),  # 昨收
                    'growth': float(d[19]),  # 涨幅
                    'amplitude': float(d[20]),  # 振动幅度
                    'volume_transaction': float(d[12]),  # 成交量
                    'turnover': float(d[13]),  # 成交额
                    'stock_code': d[1],
                    'chg': d[18],
                    'rs': 'jrj'
                }
                result.append(res)
            return result

        else:
            logging.error("【JRJ】获取[%s]实时数据出现请求错误,请求码:%s" % (codes, resp.status))
            return None


if __name__ == '__main__':
    jrj = JRJData()
    print jrj.getCurData(['603300'])
