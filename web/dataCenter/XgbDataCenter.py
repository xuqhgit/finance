# coding:utf-8

import json
import logging

from web.utils.webclient import WebClient




class XgbData(object):
    """
    选股宝
    """

    @staticmethod
    def getCurData(codes):
        """

        :param codes:列表
        :return:
        """
        url = 'https://wows-api.wallstreetcn.com/real?fields=prod_name,last_px,px_change,px_change_rate,high_px,low_px,' \
              'open_px,preclose_px,business_amount,business_balance,' \
              'market_value,turnover_ratio,dyn_pb_rate,amplitude,pe_rate,bps,hq_type_code,trade_status,bid_grp,offer_grp,' \
              'business_amount_in,business_amount_out,circulation_value,securities_type,update_time,' \
              'price_precision&en_prod_code=%s'
        client = WebClient()
        codes_c = []
        for c in codes:
            codes_c.append('%s.%s' % (c, XgbData.__stock_code_type(c)))
        resp = client.get(url % ','.join(codes_c))
        if resp.status == 200:
            da = resp.data
            data = json.loads(da)['data']['snapshot']
            print data
            result = []
            for i in range(0, len(codes_c)):
                d = data[codes_c[i]]
                res = {
                    'high_price': d[4],  # 最高
                    'low_price': d[5],  # 最低
                    'price': d[1],  # 当前价
                    'open_price': d[6],  # 开盘价
                    'turnover_rate': round(d[12], 3),  # 换手
                    'close_price': d[7],  # 昨收
                    'growth': round(d[3], 3),  # 涨幅
                    'amplitude': round(d[13], 3),  # 振动幅度
                    'volume_transaction': d[8],  # 成交量
                    'turnover': d[9],  # 成交额
                    'stock_code': codes[i],
                    'chg': round(d[2], 3),
                    'rs': 'xgb'
                }
                result.append(res)
            return result

        else:
            logging.error("【xgb】获取[%s]实时数据出现请求错误,请求码:%s" % (codes, resp.status))
            return None

    @staticmethod
    def __stock_code_type(code):
        """
        根据stock代码 获取stock类型 s  sz
        :param code:
        :return:
        """
        code_type = 'SS'
        if code[0] == '6':
            code_type = 'SS'
        elif code[0] == '0':
            code_type = 'SZ'
        elif code[0] == '3':
            code_type = 'SZ'
        return code_type


if __name__ == '__main__':
    hx = XgbData()
    print hx.getCurData(['603300'])
