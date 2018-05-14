# coding:utf-8


from web.utils.webclient import WebClient
from web.utils import StringUtils
from web.utils import THSUtils
import json
import logging
from web.dataCenter.StockDataCenter import *
from bs4 import BeautifulSoup

KEY_STOCK_LAST = 'THS:%s:%s:%s:LAST:%s'  # 日期 年 月 日股票代码
KEY_STOCK_MONEY_LAST = 'THS:%s:%s:%s:MONEY:%s'  # 日期 年 月 日 股票代码
KEY_BOND_LAST = 'THS:%s:%s:%s:BOND:%s'  # 日期 年 月 日 股票代码
KEY_FUND_LAST = 'THS:%s:%s:%s:FUND:%s'  # 日期 年 月 日 股票代码
KEY_PLATE_LAST = 'THS:%s:%s:%s:%s:%s'  # 日期 年 月 日 plate_code 股票代码
MONGO_COL_LAST_MIN = 'THS_LAST_MIN'  # mongodb collection 日时分数据
MONGO_COL_MONEY_MIN = 'THS_MONEY_MIN'  # mongodb collection 资金日时分数据
MONGO_COL_PLATE_MIN = 'THS_PLATE_MIN'  # mongodb collection 各大板块日时分数据
MONGO_COL_STOCK_HISTORY = 'THS_HISTORY'  # mongodb collection 历史数据


class THSData(StockData):
    def __init__(self):
        self.client = WebClient(
            headers={
                'Host': 'd.10jqka.com.cn',
                'Connection': 'keep-alive',
                'Cookie': 'v=%s' % THSUtils.get_v(),
                'Accept': '*/*',
                'Accept-Language': 'zh-cn',
                'Referer': 'http://m.10jqka.com.cn',
                'Cache-Control': 'max-age=0'
            })
        pass

    def getData(self, url):
        return self.client.get(url, headers={"Cookie": "v=%s" % THSUtils.get_v()})

    def getAllStockList(self):
        """
        获取所有股票基本信息 包含股票代码 股票名称
        :return:
        """
        pass

    def getAllStockPlate(self):
        """
        获取所有股票板块信息

        :return:
        """
        # url中2代表了第二页 目前还有两页数据 %s 值为 1 2
        url = "http://q.10jqka.com.cn/interface/stock/thshy/zdf/desc/%s/quote/quote"
        url_1 = url % '1'
        data = self.getData(url_1)
        result = []
        if data.status == 200:
            data_json = json.loads(data.data)['data']
            result.extend(data_json)
            pass
        else:
            logging.error("同花顺下载板块数据1出错:%s" % data.status)
        url_2 = url % '2'
        data = self.getData(url_2)
        if data.status == 200:
            data_json = json.loads(data.data)['data']
            result.extend(data_json)
            pass
        else:
            logging.error("同花顺下载板块数据2出错:%s" % data.status)
        return result

    def getAllStockConcept(self):
        """
        获取所有股票概念信息

        :return:
        """
        # %s 值可为1 2 3 4 分为4页数据
        url = "http://q.10jqka.com.cn/interface/stock/gn/zdf/desc/%s/quote/quote"
        page = [1, 2, 3, 4]
        result = []
        for i in page:
            url_i = url % i
            data = self.getData(url_i)
            if data.status == 200:
                data_json = json.loads(data.data)['data']
                result.extend(data_json)
                pass
            else:
                logging.error("同花顺下载板块数据%s出错:%s" % (i, data.status))
        return result

    def getAllStockArea(self, code):
        """
        获取股票区域数据
        :param code:
        :return:
        """
        pass

    def getStockMin(self, code):
        """
        获取指定股票时分
        :param code:
        :return:
        """
        pass

    def getStockWeek(self, code):
        """
        获取指定股票周数据
        :param code:
        :return:
        """
        pass

    def getStockMonth(self, code):
        """
        获取指定股票月数据
        :param code:
        :return:
        """
        pass

    def getStockFMin(self, code):

        pass

    def getStockConceptByCode(self, code):
        """
        通过股票代码获取当前股票概念数据
        :return:
        """
        # %s为股票code
        url = "http://d.10jqka.com.cn/v4/stockblock/hs_%s/last.js" % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)['items']
        else:
            logging.error("同花顺获取个股[%s]概念数据出错:%s" % (code, data.status))
        return None

    def getStockPlateInfoByCode(self, code):
        """
        通过股票代码获取股票当前盘口数据
        :return:
        """
        # %s为股票code
        url = "http://d.10jqka.com.cn/v5/realhead/hs_%s/last.js" % code
        data = self.getData(url)
        json_data = {}
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            json_data = json.loads(json_str)['items']
        else:
            logging.error("同花顺获取个股【%s】盘口数据出错:%s" % (code, data.status))
            return None
        try:
            # 数据转换 由于同花顺数据key字段命名难以理解 故数据转换处理一下
            result = {}
            if json_data['10'] == "":
                return None

            # 股票代码
            result['stock_code'] = u'%s' % code
            result['name'] = u'%s' % json_data['name']
            # 当前价格
            result['price'] = StringUtils.str_2_float(json_data['10'])
            # 开盘价格
            result['open_price'] = StringUtils.str_2_float(json_data['7'])
            # 昨收盘价格
            result['close_price'] = StringUtils.str_2_float(json_data['6'])
            # 最高价格
            result['high_price'] = StringUtils.str_2_float(json_data['8'])
            # 最低价格
            result['low_price'] = StringUtils.str_2_float(json_data['9'])
            # 平均价格
            result['average_price'] = StringUtils.str_2_float(json_data['1378761'])
            # 量比
            result['vp'] = StringUtils.str_2_float(json_data['1771976'])
            # 涨幅率
            result['growth'] = StringUtils.str_2_float(json_data['199112'])
            # 振幅
            result['amplitude'] = StringUtils.str_2_float(json_data['526792'])
            # 涨幅值
            result['chg'] = StringUtils.str_2_float(json_data['264648'])
            # 换手率
            result['turnover_rate'] = StringUtils.str_2_float(json_data['1968584'])
            # 买入
            result['buy_price'] = StringUtils.str_2_float(json_data['24'])
            # 卖出
            result['sell_price'] = StringUtils.str_2_float(json_data['30'])
            # 成交量
            result['volume_transaction'] = StringUtils.str_2_float(json_data['13'])
            # 成交额
            result['turnover'] = StringUtils.str_2_float(json_data['19'])
            # 涨停价
            result['high_end'] = StringUtils.str_2_float(json_data['69'])
            # 跌停价格
            result['low_end'] = StringUtils.str_2_float(json_data['70'])
            # 委比
            if "461256" in json_data:
                result['ep'] = StringUtils.str_2_float(json_data['461256'])
            else:
                result['ep'] = 0
            # 内盘
            result['volume_in'] = StringUtils.str_2_float(json_data['15'])
            # 外盘
            result['volume_out'] = StringUtils.str_2_float(json_data['14'])
            # 市盈率
            result['pe'] = StringUtils.str_2_float(json_data['2034120'])
            # 市净率
            result['pb'] = StringUtils.str_2_float(json_data['592920'])
            # 交易总额
            result['amt'] = StringUtils.str_2_float(json_data['19'])
            # 总手
            result['volume'] = StringUtils.str_2_float(json_data['13'])
            # 流通股
            if "407" in json_data:
                result['c_stock'] = StringUtils.str_2_float(json_data['407'])
            else:
                result['c_stock'] = 0

            # 流通值
            result['c_amt'] = StringUtils.str_2_float(json_data['3475914'])
            # 总股本
            if "402" in json_data:
                result['t_stock'] = StringUtils.str_2_float(json_data['402'])
            else:
                result['t_stock'] = 0
            # 总市值
            result['mc'] = StringUtils.str_2_float(json_data['3541450'])
            # 停牌 1为停牌
            result['trade_stop'] = json_data['stop']
            result['rs'] = 'ths'

        except Exception, e:
            logging.info(data.data)
            logging.error(e)

        return result

    def getStockLast(self, code):
        """
        获取股票最后交易数据
        :return:
        """
        url = 'http://d.10jqka.com.cn/v4/time/hs_%s/last.js' % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取个股[%s] LAST数据出错:%s" % (code, data.status))
        return None

    def getStockMoneyLast(self, code):
        """
        获取股票最后资金数据
        :param code:
        :return:
        """
        url = 'http://d.10jqka.com.cn/v2/moneyflow/hs_%s/last.js' % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取个股[%s] MONEY_LAST数据出错:%s" % (code, data.status))
        return None

    def getBondDailyByCode(self, code):
        """
        获取债券日数据
        :param code:
        :return:
        """
        url = '' % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取债券[%s] DAILY数据出错:%s" % (code, data.status))
        return None

    def getBondLastByCode(self, code):
        """
        获取债券日交易数据
        :param code:
        :return:
        """
        url = '' % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取债券[%s] LAST数据出错:%s" % (code, data.status))
        return None

    def getFundDailyByCode(self, code):
        """
        获取基金日数据
        :param code:
        :return:
        """
        url = '' % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取债券[%s] DAILY数据出错:%s" % (code, data.status))
        return None

    def getFundLastByCode(self, code):
        """
        获取基金日交易数据
        :param code:
        :return:
        """
        url = '' % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取债券[%s] LAST数据出错:%s" % (code, data.status))
        return None

    def getStockPlateDailyByCode(self, code):
        """
        获取股票版块daily数据 包含 行业 区域 概念
        :return:
        """
        url = 'http://d.10jqka.com.cn/v4/realhead/48_%s/last.js' % code
        data = self.getData(url)
        json_data = {}
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            json_data = json.loads(json_str)['items']
        else:
            logging.error("同花顺获取板块【%s】盘口数据出错:%s" % (code, data.status))
            return None
        try:
            # 数据转换 由于同花顺数据key字段命名难以理解 故数据转换处理一下
            result = {}
            if json_data['10'] == "":
                return None

            # 股票代码
            result['plate_code'] = u'%s' % code
            # 当前价格
            result['price'] = StringUtils.str_2_float(json_data['10'])
            # 开盘价格
            result['open_price'] = StringUtils.str_2_float(json_data['7'])
            # 昨收盘价格
            result['close_price'] = StringUtils.str_2_float(json_data['6'])
            # 最高价格
            result['high_price'] = StringUtils.str_2_float(json_data['8'])
            # 最低价格
            result['low_price'] = StringUtils.str_2_float(json_data['9'])
            # 平均价格
            result['average_price'] = StringUtils.str_2_float(json_data['1378761'])
            # 量比
            result['vp'] = StringUtils.str_2_float(json_data['1771976'])
            # 涨幅率
            result['growth'] = StringUtils.str_2_float(json_data['199112'])
            # 振幅
            result['amplitude'] = StringUtils.str_2_float(json_data['526792'])
            # 涨幅值
            result['chg'] = StringUtils.str_2_float(json_data['264648'])
            # 换手率
            result['turnover_rate'] = StringUtils.str_2_float(json_data['1968584'])
            # 上涨数
            result['up_count'] = StringUtils.str_2_float(json_data['38'])
            # 下跌
            result['down_count'] = StringUtils.str_2_float(json_data['39'])
            # 成交量
            result['volume_transaction'] = StringUtils.str_2_float(json_data['13'])
            # 成交额
            result['turnover'] = StringUtils.str_2_float(json_data['19'])
            # 持平数
            result['keep_count'] = StringUtils.str_2_float(json_data['37'])
            # 委买
            result['c_buy'] = StringUtils.str_2_float(json_data['22'])
            # 委比
            if "461256" in json_data:
                result['ep'] = StringUtils.str_2_float(json_data['461256'])
            else:
                result['ep'] = 0
            # 委卖
            result['c_sell'] = StringUtils.str_2_float(json_data['23'])

            # 市盈率
            result['pe'] = StringUtils.str_2_float(json_data['2034120'])
            # 市净率
            result['pb'] = StringUtils.str_2_float(json_data['592920'])
            # 交易总额
            result['amt'] = StringUtils.str_2_float(json_data['19'])
            # 总手
            result['volume'] = StringUtils.str_2_float(json_data['13'])

            # 流通值
            result['c_amt'] = StringUtils.str_2_float(json_data['3475914'])

            # 总市值
            result['mc'] = StringUtils.str_2_float(json_data['3541450'])
        except Exception, e:
            logging.info(data.data)
            logging.error(e)
        return result

    def getPlateLast(self, code):
        """
        获取股票最后交易数据
        :return:
        """
        url = 'http://d.10jqka.com.cn/v4/time/bk_%s/last.js' % code
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取板块[%s] LAST数据出错:%s" % (code, data.status))
        return None

    def getStockHistoryData(self, code, year, type):
        """
        data数据格式20160415,16.90,17.13,16.75,17.01,12749919,216191310.00,1.369,
        时间,开,高,低,收,成交量,成交额,换手
        获取股票历史数据
        :param code: stock code
        :param year: 年份  2016 2015
        :param type: 类型 01 当日  20 月线 10周线 30 5分线 40 半小时线 50 60分钟线 60 分钟线
        :return:
        """
        url = 'http://d.10jqka.com.cn/v3/line/hs_%s/%s/%s.js' % (code, type, year)
        data = self.getData(url)
        if data.status == 200:
            json_str = data.data.split("(", 2)[1][0:-1]
            return json.loads(json_str)
        else:
            logging.error("同花顺获取板块[%s] %s %s 数据出错:%s" % (code, year, type, data.status))
        return None


class THSDataOther(object):
    """
    同花顺其他数据
    """

    @staticmethod
    def get_stock_new(type='hszb', page=1):
        """
        获取新股数据
        :param type: 类型分为hszb zxb cyb
        :param page:
        :return:
        """
        client = WebClient()
        url = 'http://data.10jqka.com.cn/ipo/xgsgyzq/board/%s/field/SGDATE/page/%s/order/desc/ajax/1/' % (type, page)
        data = client.get(url, headers={"Cookie": "v=%s" % THSUtils.get_v()})
        list = []
        if data.status == 200:
            html = data.data.decode('gbk').encode('UTF-8')
            trs = BeautifulSoup(html, "html.parser").find(id='maintable').select("[class~=m_tbd] tr")
            for tr in trs:
                if tr is None:
                    continue
                tds = tr.select('td')
                data_json = {}
                # stock code
                data_json['code'] = tds[0].a.text.strip()
                # stock name
                data_json['name'] = tds[1].a.text.strip()
                # stock type
                data_json['type'] = type == 'hszb' and 'sh' or type
                # 申购代码
                data_json['buy_code'] = str(tds[2].string)
                # 总发行量
                data_json['public_volume'] = StringUtils.str_2_float(tds[3].string) * 10000
                # 网上发行量
                data_json['public_volume_online'] = StringUtils.str_2_float(tds[4].string) * 10000
                # 申购上限
                data_json['buy_limit'] = StringUtils.str_2_float(tds[5].string) * 10000

                # 申购需配市值
                data_json['buy_c_limit'] = str(tds[6].string)
                # 发行价
                data_json['public_price'] = StringUtils.str_2_float(tds[7].string)
                # 发行市盈率
                if tds[8].string:
                    data_json['public_pe'] = tds[8].string.replace('-', '')
                # 板块市盈率
                data_json['bank_pe'] = tds[9].string.replace('-', '')
                # 申购日期
                data_json['buy_date'] = tds[10].string[0:5].replace('-', '')
                # 中签率
                data_json['lot_winning_rate'] = StringUtils.str_2_float(tds[11].string)
                # 中签日期（缴款）
                data_json['lot_date'] = tds[13].string.replace('-', '')
                # 发行日期
                data_json['public_date'] = tds[14].string.replace('-', '')
                # 打新收益
                data_json['income'] = tds[15].string.replace('-', '0')
                # 涨停数
                data_json['high_count'] = tds[16].string.replace('-', '0')

                list.append(data_json)
            return list
        else:
            logging.error("同花顺获取stock new [%s] 数据出错:%s" % (type, data.status))
        return None

    @staticmethod
    def get_stock_important_event(code, url=None, count=0):
        result = []
        if count > 1:
            return result

        client = WebClient()
        if url is None:
            url = "http://basic.10jqka.com.cn/mobile/%s/reminddetailn.html" % code
        data = client.get(url)

        if data.status == 200:
            html = data.data.decode('gbk').encode('UTF-8')
            bs = BeautifulSoup(html.replace("</h1> </a>", "</h1>").replace("</a> </a>", "</a>"), "html.parser")
            div_list = bs.select("[class~=yearlist]")
            for div in div_list:
                data_json = {}
                mdate = str(div.select("[class~=mdate]")[0].string).strip()
                myear = str(div.select("[class~=myear]")[0].string).strip()
                data_json['stock_code'] = code
                data_json['event_code'] = '000000'
                data_json['event_date'] = '%s%s' % (myear, mdate.replace("-", ""))
                data_json['type'] = div.attrs['flag']
                if div.h1:
                    data_json['name'] = div.h1.string.strip()
                elif div.a:
                    data_json['name'] = div.a.string.strip()
                if div.p:
                    data_json['content'] = div.p.text.replace('\r', '').replace('\t', '').replace('\n', '').strip()
                result.append(data_json)
        else:
            logging.error("同花顺获取stock event [%s] 数据出错:%s" % (code, data.status))
            if count == 0:
                logging.error("同花顺获取stock event [%s] 切换地址" % code)
                THSDataOther.get_stock_important_event(code,
                                                       url="http://basic.10jqka.com.cn/mobile/%s/pubn.html#jumpaction=iframe" % code,
                                                       count=count + 1)
        return result


if __name__ == '__main__':
    print THSDataOther.get_stock_important_event("002606")
    # pass
