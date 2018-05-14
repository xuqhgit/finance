# coding:utf-8

import json
import logging

from web.utils.webclient import WebClient

client = WebClient()


class HexunData(object):
    """
    和讯网
    """

    @staticmethod
    def getCurData(codes):
        """

        :param codes:列表
        :return:
        """
        url = 'http://webstock.quote.hermes.hexun.com/a/quotelist?code=%s&callback=callback&column=DateTime,LastClose,' \
              'Open,High,Low,Price,Volume,Amount,LastSettle,SettlePrice,OpenPosition,ClosePosition,BuyPrice,BuyVolume,SellPrice,' \
              'SellVolume,PriceWeight,EntrustRatio,UpDown,EntrustDiff,UpDownRate,OutVolume,InVolume,AvePrice,VolumeRatio,PE,' \
              'ExchangeRatio,LastVolume,VibrationRatio,DateTime,OpenTime,CloseTime'
        codes_c = []
        for c in codes:
            codes_c.append('%sse%s' % (HexunData.__stock_code_type(c), c))
        resp = client.get(url % ','.join(codes_c))
        if resp.status == 200:
            da = resp.data[9:len(resp.data) - 2].decode("gbk").encode("utf-8")
            data = json.loads(da)['Data']
            result = []
            for i in range(0, len(data)):
                d = data[0][i]
                res = {
                    'high_price': d[3]/100.00,  # 最高
                    'low_price': d[4]/100.00,  # 最低
                    'price': d[5]/100.00,  # 当前价
                    'open_price': d[2]/100.00,  # 开盘价
                    'average_price': d[23]/100.00,  # 均价
                    'turnover_rate': d[26]/100.00,  # 换手
                    'close_price': d[1]/100.00,  # 昨收
                    'growth': d[20]/100.00,  # 涨幅
                    'amplitude': d[28]/100.00,  # 振动幅度
                    'volume_transaction': d[6],  # 成交量
                    'turnover': d[7],  # 成交额
                    'stock_code': codes[i],
                    'chg': d[18]/100.00,
                    'rs': 'hexun'
                }
                result.append(res)
            return result

        else:
            logging.error("【Hexun】获取[%s]实时数据出现请求错误,请求码:%s" % (codes, resp.status))
            return None

    @staticmethod
    def __stock_code_type(code):
        """
        根据stock代码 获取stock类型 s  sz
        :param code:
        :return:
        """
        code_type = None
        if code[0] == '6':
            code_type = 's'
        elif code[0] == '0':
            code_type = 'sz'
        elif code[0] == '3':
            code_type = 'sz'
        return code_type


if __name__ == '__main__':
    hx = HexunData()
    print hx.getCurData(['603300'])
