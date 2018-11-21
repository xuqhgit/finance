# coding:utf-8
from web.utils import EmailSend
from web.utils.StockFile import StockFile
from web.utils import TemplateUtils
from web.db.dbexec import DBExec
from web.dataCenter import THSDataCenter
from web.dataCenter import StockData
import json
from web.busi.StockAnalysis import *
from web.busi import StockAnalysis
from web.utils import Holiday
import logging
from web.db import Query

CUR_PUBLIC_NEW_STOCK = {"1970-01-01": []}
stockFile = StockFile()


class StockService(object):
    def __init__(self):
        self.thsData = THSDataCenter.THSData()
        self.thsDataOther = THSDataCenter.THSDataOther()
        self.db = DBExec(Query.QUERY_STOCK, "")
        pass

    def saveAllDailyStocks(self, stock_list=[], single=False, handleSize=300):
        """
        保存daily stock 数据
        :return:
        """
        db = DBExec(Query.QUERY_STOCK, "")
        if bool(stock_list) is False and single is False:
            stock_list = db.setId("FIND_STOCK_ALL").execute(None)
        if bool(stock_list) is False:
            logging.info("保存当日stock daily数据：无数据需处理")
        result_data = []
        CommonUtils.start_many_thread(stock_list, handleSize=handleSize, args=(result_data,),
                                      target=self.getAllDailyStocks,
                                      asyn=False, name='保存stock daily 数据')
        db_result = db.setId("SAVE_DAILY_STOCK").execute(result_data)
        logging.info("插入数据:%s条" % db_result)
        db.commitTrans()
        StockData.refresh_stock_last_day(result_data)
        return result_data

    def getAllDailyStocks(self, list, result):
        center = THSDataCenter.THSData()
        r = []
        cur_date = Holiday.get_cur_date()
        for s in list:
            code = s['code']
            d = center.getStockPlateInfoByCode(code)
            print d
            if d:
                d['trade_date'] = cur_date
                r.append(d)
        result.extend(r)
        pass

    def saveAllDailyStocksLast(self, stock_list=[], single=False, handleSize=300):
        """
        保存所有股票当日数据 包含资金等
        :return:
        """
        result_data = []
        if bool(stock_list) is False and single is False:
            db = DBExec(Query.QUERY_STOCK, "")
            stock_list = db.setId("FIND_STOCK_ALL").execute(None)
        if bool(stock_list) is False:
            logging.info("保存当日stock 十分数据：无数据需处理")

        CommonUtils.start_many_thread(stock_list, args=(result_data,), handleSize=handleSize,
                                      target=self.saveDailyStocksLast,
                                      name='保存stock last and money 数据', asyn=False)
        return result_data

    def saveDailyStocksLast(self, list, result):
        """
        保存最新股票交易数据到file中 还有 资金数据
        :param list:
        :return:
        """
        center = THSDataCenter.THSData()
        for s in list:
            code = s['code']
            d = center.getStockLast(code)
            if d:
                h_code = 'hs_%s' % code
                last_date = d[h_code]['date']

                try:
                    stockFile.write_stock_json(d, code, last_date)
                    result.append({'code': code})
                except Exception, e:
                    logging.error(e)
                d = center.getStockMoneyLast(code)
                if d:
                    try:
                        stockFile.write_stock_money_json(d, code, last_date)
                    except Exception, e:
                        logging.error(e)
            else:
                logging.error("未获取到StocksLast:%s" % code)
        pass

    def saveAllDailyPlate(self):
        """
        保存所有板块日数据 包含 区域 行业 概念
        :return:
        """
        plate_list = self.db.setId("FIND_PLATE_ALL").execute(None)
        result = []
        CommonUtils.start_many_thread(plate_list, handleSize=100, args=(result,), target=self.getAllDailyPlate,
                                      asyn=False, name='所有板块daily日数据')
        db_result = self.db.setId("SAVE_DAILY_PLATE").execute(result)
        logging.info("[saveAllDailyPlate]插入数据:%s条" % db_result)
        self.db.commitTrans()
        return db_result

    def getAllDailyPlate(self, list, result):
        """
        获取集合中所有版块的数据
        :param list:
        :param result:
        :return:
        """
        center = THSDataCenter.THSData()
        r = []
        cur_date = Holiday.get_cur_date()
        for s in list:
            code = s['code']
            d = center.getStockPlateDailyByCode(code)
            if d:
                d['trade_date'] = cur_date
                r.append(d)
        result.extend(r)
        pass

    def saveAllDailyPlateLast(self):
        """
        保存所有股票当日数据 包含资金等
        :return:
        """
        plate_list = self.db.setId("FIND_PLATE_ALL").execute(None)
        self.saveDailyPlateLast(plate_list)
        logging.info("下载PLATE_LAST数据完成")

    def saveDailyPlateLast(self, list):
        """
        保存最新股票板块交易数据到file中
        :param list:
        :return:
        """
        try:
            center = THSDataCenter.THSData()
            for s in list:
                code = s['code']
                plate_data = center.getPlateLast(code)
                if plate_data:
                    h_code = 'bk_%s' % code
                    last_date = plate_data[h_code]['date']
                    try:
                        stockFile.write_stock_json(plate_data, code, last_date)
                    except Exception, e:
                        logging.error(e)
        except Exception, e:
            logging.error("保存板块信息异常")
            logging.error(e)

    def saveStockNew(self, page=1):
        """
        更新新股
        :return:

        """
        type = ('hszb', 'zxb', 'cyb')
        result = []
        for t in type:
            r = THSDataCenter.THSDataOther.get_stock_new(type=t, page=page)
            if r:
                result.extend(r)
            pass
        count = self.db.setId("SAVE_STOCK_NEW_TEMP").execute(result)
        self.db.commitTrans()
        # 清空表
        self.db.setId('CLEAR_STOCK_NEW_TEMP').execute(None)
        self.db.commitTrans()
        return count

    def getStockHistoryData(self, code, year, type):
        """
        获取stock 历史数据
        :param code: stock code
        :param year: 年份
        :param type: 类型
        :return:
        """

        ths = THSDataCenter.THSData()
        data = ths.getStockHistoryData(code, year, type)
        return data

    def saveStockBlockData(self):
        """
        保存每个Stock 概念数据
        :return:
        """
        stock_list = self.db.setId("FIND_STOCK_ALL").execute(None)
        result = []
        CommonUtils.start_many_thread(stock_list, args=(result,), target=self.getStockBlockData,
                                      asyn=False, name='获取Stock 概念数据')

        logging.info("[STOCK BLOCK] 应插入数据:%s条" % len(result))
        db_result = self.db.setId("SAVE_STOCK_PLATE_TEMP").execute(result)
        logging.info("[STOCK BLOCK] 插入数据:%s条" % db_result)
        # 插入 stock_plate
        insert_count = self.db.setId("INSERT_STOCK_PLATE").execute(None)
        logging.info("[STOCK BLOCK] 插入STOCK_PLATE数据:%s条" % insert_count)

        # 更新 stock_plate
        update_count = self.db.setId("UPDATE_STOCK_PLATE").execute(None)
        logging.info("[STOCK BLOCK] 更新STOCK_PLATE数据:%s条" % update_count)

        # 同步 plate
        insert_count = self.db.setId("SYN_INSERT_PLATE").execute(None)
        logging.info("[STOCK BLOCK] 同步SYN_INSERT_PLATE数据:%s条" % insert_count)

        # 清理 stock_plate_temp
        clear_count = self.db.setId("CLEAR_STOCK_PLATE_TEMP").execute(None)
        logging.info("[STOCK BLOCK] 清理STOCK_PLATE数据:%s条" % clear_count)
        #
        self.db.commitTrans()

        return db_result

    def getStockBlockData(self, list, result):
        """
        获取多个stock 概念数据
        :param list:
        :param result:
        :return:
        """
        center = THSDataCenter.THSData()
        r = []
        for s in list:
            code = s['code']
            d = center.getStockConceptByCode(code)
            if d:
                for item in d:
                    r.append({'stock_code': code, "plate_code": item["id"], "plate_name": item["name"]})
        result.extend(r)
        pass

    def getCurYearPublic(self, code):
        """
        获取今年发行的Stock时间并且获取45日数据
        :param code:
        :return:
        """
        data = self.getStockHistoryData(code, Holiday.get_cur_year(), "01")
        if data is None:
            return None
        arr = StringUtils.str_2_arr(data['data'].split(";"))
        if len(arr) > 2:
            first = arr[0]
            second = arr[1]
            result = (first[4] - first[1]) * 100 / first[1]
            if first[0] > 20160301 and ((result > 11.5 and first[4] == first[2]) or (result == 0 and first[7] < 0.1)) \
                    and second[3] == second[2]:
                return arr[0:45]
        return None

    def getCurYearPublicList(self):
        """

        :return:
        """
        result = []
        stock_list = self.db.setId("FIND_STOCK_NEW").execute(None)
        CommonUtils.start_many_thread(stock_list, args=(result,), target=self.__getBatchCurYearPublic,
                                      asyn=False, name='获取当年的new stock')
        return BusinessAnalysis.analysisPublicData(result)

    def __getBatchCurYearPublic(self, list, result):
        """
        批量获取数据
        :param list:
        :param result:
        :return:
        """
        r = []
        for s in list:
            code = s['code']
            d = self.getCurYearPublic(code)
            if d:
                r.append({'code': code, "data": d})
        result.extend(r)
        pass

    def curTaskExecuteInfo(self):
        cur_date = Holiday.get_cur_date()

        result = {"date": "%s" % cur_date,
                  "stock_daily_count": self.db.setId("COUNT_STOCK_DAILY").execute({'date': cur_date}),
                  "plate_daily_count": self.db.setId("COUNT_PLATE_DAILY").execute({'date': cur_date})}
        return result

    def checkPublicNewStockStatus(self):
        cur_date = Holiday.get_cur_date()
        data = None
        center = THSDataCenter.THSData()
        size = 0
        for code in CUR_PUBLIC_NEW_STOCK:
            data = CUR_PUBLIC_NEW_STOCK[code]
            if code != cur_date:
                del (CUR_PUBLIC_NEW_STOCK[code])
                CUR_PUBLIC_NEW_STOCK[cur_date] = list(self.db.setId("FIND_PUBLIC_NEW_STOCK").execute(None))
                data = CUR_PUBLIC_NEW_STOCK[cur_date]
                size = len(data)
        logging.info(str(CUR_PUBLIC_NEW_STOCK))
        stock_arr = []
        for i in range(0, size):
            d = data[i]
            if d['code'] is None:
                continue
            try:
                stock_data = center.getStockPlateInfoByCode(d['code'])
                high_end = stock_data['high_end']
                cur_price = stock_data['price']
                if cur_price != high_end:
                    stock_data['high_count'] = d['high_count']
                    logging.info(stock_data)
                    stock_arr.append(stock_data)
                    d['code'] = None
            except Exception, e:
                logging.error("%s" % e)
        if len(stock_arr) > 0:
            logging.info(str(stock_arr))
            email_content = TemplateUtils.get_email("new_stock", stock_arr)
            if email_content:
                try:
                    EmailSend.send(email_content, 'PUBLIC', subtype='html')
                except Exception, e:
                    logging.error("发送邮件失败：%s" % e)
            else:
                logging.error("发送邮件内容异常")
        pass

    def checkStopStockCode(self):
        stop_list = list(self.db.setId("FIND_RESUMPTION_STOCK").execute(None))
        # stop_list = [{'code':'002606'}]
        center = THSDataCenter.THSData()
        # 获取当前上证指数 当前中小板指数

        type_code = {'zxb': '399001', 'sh': '1A0001'}
        result = []
        for i in range(0, len(stop_list)):
            code = stop_list[i]['code']
            stock_data = center.getStockPlateInfoByCode(code)
            if stock_data and stock_data['trade_stop'] == 0:
                data = StockData.get_stock_last_day(code)
                if data:
                    arr = data[len(data) > 1 and len(data) - 2 or len(data) - 1]
                    stock_data['last'] = arr
                    result.append(stock_data)
        if len(result) > 0:
            # result.append(str(sh))
            # result.append(str(sz))
            content = TemplateUtils.get_email("stop_stock", result)
            if content:
                EmailSend.send(content, 'STOP', subtype='html')

    def __findLastNewStock(self):
        return list(self.db.setId("FIND_LAST_NEW_STOCK").execute(None))

    def getLastNewStockData(self):
        last_new_list = self.__findLastNewStock()
        center = THSDataCenter.THSData()
        result = []
        if last_new_list is None:
            return None
        for i in range(0, len(last_new_list)):
            code = last_new_list[i]['code']
            year_type = center.getStockHistoryData(code, 'last', '01')
            if year_type is None:
                continue
            year_type_data = year_type['data']
            arr = StringUtils.str_2_arr(year_type_data.split(";"))
            data_count = 7
            count = data_count
            start = False
            data = []
            for j in range(1, len(arr)):
                if start is False:
                    if arr[j][2] != arr[j][3]:
                        start = True
                    else:
                        continue
                if len(data) == 0:
                    last_new_list[i]['last_close_price'] = arr[j - 1][4]
                data.append(arr[j])
                count -= 1
                if count <= 0:
                    break
            if len(data) == 0 or len(data) != data_count:
                stock_data = center.getStockPlateInfoByCode(code)
                if stock_data:
                    flag = False
                    if len(data) == 0:
                        if stock_data['high_price'] != stock_data['low_price']:
                            flag = True
                        elif stock_data['high_price'] == stock_data['low_price'] and stock_data['growth'] < 0:
                            flag = True
                    else:
                        flag = True
                    if flag:
                        # 时间, 开, 高, 低, 收, 成交量, 成交额, 换手
                        if len(data) == 0:
                            last_new_list[i]['last_close_price'] = stock_data['close_price']
                        data.append(['-', stock_data['open_price'], stock_data['high_price'], stock_data['low_price'],
                                     stock_data['price'], stock_data['volume_transaction'], stock_data['turnover'],
                                     stock_data['turnover_rate']])
            if len(data) != 0:
                last_new_list[i]['data'] = data
                result.append(last_new_list[i])
        return result

    def get_stock_buy_data(self):
        """
        获取购买数据
        :return:
        """
        data = DBExec(Query.QUERY_STOCK_BUY, "GET_STOCK_BUY").execute(None)
        if type(data) != list:
            data = [data]
        result = []
        sh = self.thsData.getStockPlateInfoByCode('1A0001')
        sz = self.thsData.getStockPlateInfoByCode('399001')
        result.append({"p": sh['price'], "h": sh['high_price'], "k": sh['open_price'], "l": sh['low_price'],
                       "s": sh['turnover_rate'], "z": sh['growth'], "t": "h", 'a': round(sh['amt'] / 100000000, 2)})
        result.append({"p": sz['price'], "h": sz['high_price'], "k": sz['open_price'], "l": sz['low_price'],
                       "s": sz['turnover_rate'], "z": sz['growth'], "t": "h", 'a': round(sz['amt'] / 100000000, 2)})
        for d in data:
            stock_code = d['stock_code']
            stock_data = StockData.get_stock_cur_trade(stock_code)
            # 当前价格 当前换手 当前涨幅 营收
            result.append(
                {"p": stock_data['price'], "h": stock_data['high_price'], "k": stock_data['open_price'],
                 "l": stock_data['low_price'], "s": stock_data['turnover_rate'], "z": stock_data['growth'],
                 'ys': round((stock_data['price'] - float(d['buy_price'])) * d['quantity'], 3)})
        return result

    def get_plate(self, params):
        """

        :param params:
        :return:
        """
        return self.db.setId("GET_PLATE_BY_PARAMS").execute(params)

    def search(self, params):
        param_flag = False
        for k in params:
            if k != 'plate_count' and bool(params[k]):
                param_flag = True
                break

        if param_flag is False:
            params['stock_buy'] = True
        if params['stock_filter']:
            params['filter_param'] = json.loads(params['stock_filter'])
        else:
            params['filter_param'] = None
        if params['codes']:
            params['codes'] = params['codes'].split(",")
        if params['type']:
            params['type'] = params['type'].split(",")
        if params['names']:
            params['names'] = params['names'].split(",")
        trade_date = self.db.setId("STOCK_DAILY_MAX").execute(None)
        params['trade_date'] = trade_date['trade_date']
        if 'stock_filter_flag' in params and bool(params['stock_filter_flag']):
            params['stock_list'] = self.getStockFilter(params)
            if bool(params['stock_list']) is False:
                params['stock_list'] = ['no']
        result = self.db.setId("STOCK_SEARCH").execute(params, params)
        if len(result) == 0:
            return result
        temp = {}
        code_list = []
        for i in range(0, len(result)):
            code_list.append(result[i]['code'])
            temp[result[i]['code']] = result[i]
            result[i]['buy_price'] = result[i]['buy_price'] and float(result[i]['buy_price']) or 0
            result[i]['fund_quantity'] = result[i]['fund_quantity'] and float(result[i]['fund_quantity']) or 0
            result[i]['fund_mc'] = result[i]['fund_mc'] and float(result[i]['fund_mc']) or 0
        plate_list = self.db.setId("STOCK_PLATE_LIST").execute(code_list)
        for i in range(0, len(plate_list)):
            c = temp[plate_list[i]['stock_code']]
            c['plate_name'] = plate_list[i]['plate_name']
            c['plate_code'] = plate_list[i]['plate_code']
        code_len = len(code_list)
        filter_condition = None
        CommonUtils.start_many_thread(code_list, handleSize=int(code_len / (code_len > 7 and 8 or code_len)),
                                      args=(temp, filter_condition),
                                      target=self.__get_stock_cur_trade,
                                      asyn=False, name='获取stock 当前信息')
        sh = self.thsData.getStockPlateInfoByCode('1A0001')
        sz = self.thsData.getStockPlateInfoByCode('399001')
        header_code_arr = [
            {'code': '1A0001', 'name': '上证', 'cur': sh and sh or {}},
            {'code': '399001', 'name': '深证', 'cur': sz and sz or {}}
        ]
        self.__handle_growth(header_code_arr)
        header_code_arr.extend(result)
        return header_code_arr

    def __handle_growth(self, header_code_arr):
        for i in range(0, len(header_code_arr)):
            h_data = StockData.get_stock_last_day(header_code_arr[i]['code'])
            header_code_arr[i]['avg'] = StockAnalysis.growth_Analysis(h_data, avgs=[5, 10, 20])

    def __get_stock_cur_trade(self, code_list, temp, filter_condition):
        """
        获取当前交易
        :param code_list:
        :param temp:
        :param filter_condition: 过滤条件
        :return:
        """
        for i in range(0, len(code_list)):
            try:
                s = StockData.get_stock_cur_trade(code_list[i])
                temp[code_list[i]]['cur'] = bool(s) and s or {}
                self.__handle_growth([temp[code_list[i]]])
            except Exception, e:
                temp[code_list[i]]['cur'] = {}
                logging.error("获取当前交易：%s" % e)

    def get_stock_old_daily(self, params):
        if params is None:
            params = {"limit": 10}
        stock_daily_list = DBExec(Query.QUERY_STOCK, "FIND_STOCK_DAILY_BY_CODE").execute(params)
        result = []
        if stock_daily_list:
            stock_daily_list.reverse()
            for a in stock_daily_list:
                d = stockFile.get_stock_json(a['stock_code'], a['stock_code'])
                # 分析当天数据成交量的数据
        return result

    def updat_stock_tfp(self):
        """
        更新停复牌
        :return:
        """
        data_list = StockData.get_cur_stock_tfp(sType='tp')
        # 更新停牌数据
        DBExec(Query.QUERY_STOCK, "UPDATE_STOCK_TFP").execute(data_list)
        data_list = StockData.get_cur_stock_tfp(sType='fp')
        # 更新复牌数据
        DBExec(Query.QUERY_STOCK, "UPDATE_STOCK_TFP").execute(data_list)

    def save_stock_lift(self):
        """
        保存解禁数据
        :return:
        """

        stock_list = DBExec(Query.QUERY_STOCK_LIFT, "NOT_IN_STOCK_LIFT").execute({'count': 8})
        # stock_list = [{'code':'600565'}]
        if bool(stock_list) is False:
            logging.error("解禁数据获取失败")
            return
        for i in range(0, len(stock_list)):
            data_list = StockData.get_stock_history_lift(stock_list[i]['code'])
            # 保存数据
            DBExec(Query.QUERY_STOCK_LIFT, "INSERT_STOCK_LIFT").execute(data_list)

    def save_stock_future_lift(self):
        """
        保存解禁数据
        :return:
        """

        data_list = StockData.get_stock_future_lift("2019-01-01", "2020-03-03")
        print data_list
        # 保存数据
        DBExec(Query.QUERY_STOCK_LIFT, "INSERT_STOCK_LIFT").execute(data_list)

    def getStockFilter(self, params):
        """

        :return:
        """
        result_data = []
        logging.info("过滤数据开始")
        stock_list = self.db.setId("STOCK_SEARCH").execute(params)
        # stock_list=[{'code':'000587'}]
        CommonUtils.start_many_thread(stock_list, args=(result_data, params), target=self.__getStockFilter,
                                      asyn=False, name='stock filter')
        logging.info("过滤stock完成：%s" % result_data)
        return result_data

    def __getStockFilter(self, stock_list, res, params):
        for s in stock_list:
            try:
                res_flag, a, d = StockAnalysis.stock_filter(s['code'], params['filter_param'])
                if res_flag:
                    res.append(s['code'])
                    logging.info("数据命中：%s" % s['code'])
            except Exception, e:
                logging.error("[%s]数据过滤异常：%s" % (s['code'], e))

    def save_stock_money(self):
        """
        保存解禁数据
        :return:
        """
        stock_list = self.db.setId("GET_ALL_STOCK").execute(None)
        # stock_list = [{'code':'603677'}]
        for i in range(0, len(stock_list)):
            try:
                data_list = StockData.get_stock_money(stock_list[i]['code'])
                # 保存数据
                if bool(data_list):
                    DBExec(Query.QUERY_STOCK_MONEY, "INSERT_STOCK_MONEY").execute(data_list)
            except Exception, e:
                logging.error("保存资金流入异常：%s" % e)


if __name__ == '__main__':
    # result = list(DBExec(QUERY_PATH, "FIND_LAST_NEW_STOCK").execute(None))
    # print result
    # center = THSDataCenter.THSData()
    # code = "603986"
    # data = center.getStockMoneyLastgetStockMoneyLast(code)
    # h_code = 'hs_%s' % code
    # last_date = data[h_code]['date']
    # stockFile.write_stock_money_json(data, code+"_money", last_date)
    # print stockFile.get_stock_money_json(code,last_date)
    # s = StockService()
    # print s.thsData.getStockPlateInfoByCode('1A0001')
    # pass
    # 分析涨幅数据
    # h_data = StockData.get_stock_last_day('601838')
    # print StockAnalysis.growth_Analysis(h_data, avgs=[5, 10, 20])

    # result = StockService().saveAllDailyStocks(stock_list=[{'code': '603843'}])
    # data = result
    # print data
    # a = [data[i]['stock_code'] for i in range(0, len(data))]
    # print a
    StockService().save_stock_lift()
    pass
    # center = THSDataCenter.THSData()
    # data = center.getStockHistoryData('603986', 'last', '01')
    # data = data['data']
    # arr = StringUtils.str_2_arr(data.split(";"))
    # last = arr[-1]
    # year = str(last[0])[0:4]
    # z_cache = {}
    # if z_cache.has_key('%s_%s' % (type, year)) is not True:
    #     print False
    # print year
