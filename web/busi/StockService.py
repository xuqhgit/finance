# coding:utf-8




from web.utils import EmailSend
from web.utils.StockFile import StockFile
from web.db.dbexec import DBExec
from web.db.RedisClient import RedisClient
from web.dataCenter import THSDataCenter
from web.busi.StockAnalysis import *
from threading import Thread
import thread
import json
import time
import logging
from web.db import MongoDBClient

QUERY_PATH = 'query/STOCK.xml'

CUR_PUBLIC_NEW_STOCK = {"1970-01-01": []}
stockFile = StockFile()


class StockService(object):
    def __init__(self):
        pass

    def saveAllDailyStocks(self):
        """
        保存daily stock 数据
        :return:
        """

        db = DBExec(QUERY_PATH, "FIND_STOCK_ALL")
        stock_list = db.execute(None)
        size = len(stock_list)
        result = []

        list_len = 200
        if size > 6000:
            list_len = 300
        count = size / list_len + (size % list_len == 0 and 0 or 1)
        thread_list = []
        logging.info("开启线程数:%s" % count)
        for i in range(0, count):
            if i == count - 1:
                t = Thread(target=self.getAllDailyStocks, args=(stock_list[i * list_len:], result))
                t.start()
            else:
                t = Thread(target=self.getAllDailyStocks,
                           args=(stock_list[(i * list_len):((i + 1) * list_len)], result))
                t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        logging.info("线程数 %s 执行完成" % count)
        db.set(QUERY_PATH, "SAVE_DAILY_STOCK")
        logging.info("应插入数据:%s条" % size)
        db_result = db.execute(result)
        logging.info("插入数据:%s条" % db_result)
        db.commitTrans()
        return db_result

    def getAllDailyStocks(self, list, result):
        center = THSDataCenter.THSData()
        r = []
        cur_date = time.strftime('%Y%m%d', time.localtime(time.time()))
        for s in list:
            code = s['code']
            d = center.getStockPlateInfoByCode(code)
            if d:
                d['trade_date'] = cur_date
                r.append(d)
        result.extend(r)
        pass

    def saveAllDailyStocksLast(self):
        """
        保存所有股票当日数据 包含资金等
        :return:
        """
        db = DBExec(QUERY_PATH, "FIND_STOCK_ALL")
        stock_list = db.execute(None)
        size = len(stock_list)
        list_len = 500
        if size > 6000:
            list_len = 300
        count = size / list_len + (size % list_len == 0 and 0 or 1)
        # thread_list = []
        # logging.info("下载STOCK_LAST开启线程数:%s" % count)
        # for i in range(0, count):
        #     logging.info(i)
        #     if i == count - 1:
        #         t = Thread(target=self.saveDailyStocksLast, args=(stock_list[i * list_len:], None))
        #         t.start()
        #     else:
        #         t = Thread(target=self.saveDailyStocksLast,
        #                    args=(stock_list[(i * list_len):((i + 1) * list_len)], None))
        #         t.start()
        #     thread_list.append(t)
        # for t in thread_list:
        #     t.join()
        self.saveDailyStocksLast(stock_list, None)
        logging.info("下载STOCK_LAST数据完成")
        pass

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
        db = DBExec(QUERY_PATH, "FIND_PLATE_ALL")
        plate_list = db.execute(None)

        size = len(plate_list)
        result = []

        list_len = 100
        count = size / list_len + (size % list_len == 0 and 0 or 1)
        thread_list = []
        logging.info("[saveAllDailyPlate]开启线程数:%s" % count)
        for i in range(0, count):
            if i == count - 1:
                t = Thread(target=self.getAllDailyPlate, args=(plate_list[i * list_len:], result))
                t.start()
            else:
                t = Thread(target=self.getAllDailyPlate,
                           args=(plate_list[(i * list_len):((i + 1) * list_len)], result))
                t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        logging.info("[saveAllDailyPlate]线程数 %s 执行完成" % count)
        db.set(QUERY_PATH, "SAVE_DAILY_PLATE")
        logging.info("[saveAllDailyPlate]应插入数据:%s条" % size)
        db_result = db.execute(result)
        logging.info("[saveAllDailyPlate]插入数据:%s条" % db_result)
        db.commitTrans()
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
        cur_date = time.strftime('%Y%m%d', time.localtime(time.time()))
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
        db = DBExec(QUERY_PATH, "FIND_PLATE_ALL")
        plate_list = db.execute(None)
        size = len(plate_list)
        list_len = 300
        count = size / list_len + (size % list_len == 0 and 0 or 1)
        thread_list = []
        # logging.info("下载PLATE_LAST开启线程数:%s" % count)
        # for i in range(0, count):
        #     if i == count - 1:
        #         t = Thread(target=self.saveDailyPlateLast, args=(plate_list[i * list_len:], None))
        #         t.start()
        #     else:
        #         t = Thread(target=self.saveDailyPlateLast,
        #                    args=(plate_list[(i * list_len):((i + 1) * list_len)], None))
        #         t.start()
        #     thread_list.append(t)
        # for t in thread_list:
        #     t.join()
        self.saveDailyPlateLast(plate_list, None)
        logging.info("下载PLATE_LAST数据完成")
        return size

    def saveDailyPlateLast(self, list, result):
        """
        保存最新股票板块交易数据到file中
        :param list:
        :return:
        """
        center = THSDataCenter.THSData()
        for s in list:
            code = s['code']
            d = center.getPlateLast(code)

            if d:
                h_code = '48_%s' % code
                last_date = d[h_code]['date']
                try:
                    stockFile.write_stock_json(d, code, last_date)
                except Exception, e:
                    logging.error(e)
        pass

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
        db = DBExec(QUERY_PATH, "SAVE_STOCK_NEW_TEMP")
        count = db.execute(result)
        db.commitTrans()
        # 清空表
        db.set(QUERY_PATH, 'CLEAR_STOCK_NEW_TEMP')
        db.execute(None)
        db.commitTrans()
        return count

    def getStockHistoryData(self, code, year, type):
        """
        获取stock 历史数据
        :param code: stock code
        :param year: 年份
        :param type: 类型
        :return:
        """
        id = "STOCK_H_%s_%s_%s" % (code, year, type)
        data = MongoDBClient.get_client(THSDataCenter.MONGO_COL_STOCK_HISTORY).find_one({"_id": id})
        if data:
            return data
        ths = THSDataCenter.THSData()
        data = ths.getStockHistoryData(code, year, type)
        if data:
            pass
            # todo MongoDBClient.insert_json(id, data, THSDataCenter.MONGO_COL_STOCK_HISTORY)
        else:
            return None
        return data

    def saveStockBlockData(self):
        """
        保存每个Stock 概念数据
        :return:
        """
        db = DBExec(QUERY_PATH, "FIND_STOCK_ALL")
        stock_list = db.execute(None)
        size = len(stock_list)
        result = []

        list_len = 200
        if size > 6000:
            list_len = 300
        count = size / list_len + (size % list_len == 0 and 0 or 1)
        thread_list = []
        logging.info("[STOCK BLOCK] 开启线程数:%s" % count)
        for i in range(0, count):
            if i == count - 1:
                t = Thread(target=self.getStockBlockData, args=(stock_list[i * list_len:], result))
                t.start()
            else:
                t = Thread(target=self.getStockBlockData,
                           args=(stock_list[(i * list_len):((i + 1) * list_len)], result))
                t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        logging.info("[STOCK BLOCK] 线程数 %s 执行完成" % count)
        db.set(QUERY_PATH, "SAVE_STOCK_PLATE_TEMP")
        logging.info("[STOCK BLOCK] 应插入数据:%s条" % len(result))
        db_result = db.execute(result)
        logging.info("[STOCK BLOCK] 插入数据:%s条" % db_result)
        # 插入 stock_plate
        db.set(QUERY_PATH, "INSERT_STOCK_PLATE")
        insert_count = db.execute(None)
        logging.info("[STOCK BLOCK] 插入STOCK_PLATE数据:%s条" % insert_count)

        # 更新 stock_plate
        db.set(QUERY_PATH, "UPDATE_STOCK_PLATE")
        update_count = db.execute(None)
        logging.info("[STOCK BLOCK] 更新STOCK_PLATE数据:%s条" % update_count)

        # 清理 stock_plate_temp
        db.set(QUERY_PATH, "CLEAR_STOCK_PLATE_TEMP")
        clear_count = db.execute(None)
        logging.info("[STOCK BLOCK] 清理STOCK_PLATE数据:%s条" % clear_count)

        db.commitTrans()
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
                    r.append({'stock_code': code, "plate_code": item["id"]})
        result.extend(r)
        pass

    def getCurYearPublic(self, code):
        """
        获取今年发行的Stock时间并且获取45日数据
        :param code:
        :return:
        """
        data = self.getStockHistoryData(code, "2016", "01")
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
        保存每个Stock 概念数据
        :return:
        """
        result = []
        db = DBExec(QUERY_PATH, "FIND_STOCK_NEW")
        stock_list = db.execute(None)
        thread_size = CommonUtils.start_many_thread(stock_list, result=result, target=self.__getBatchCurYearPublic)
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
        cur_date = time.strftime('%Y%m%d', time.localtime(time.time()))
        db = DBExec(QUERY_PATH, "COUNT_STOCK_DAILY")
        result = {"date": "%s" % cur_date}
        result['stock_daily_count'] = db.execute({'date': cur_date})
        db.set(QUERY_PATH, "COUNT_PLATE_DAILY")

        result['plate_daily_count'] = db.execute({'date': cur_date})

        return result

    def checkPublicNewStockStatus(self):
        cur_date = time.strftime('%Y%m%d', time.localtime(time.time()))
        data = None
        center = THSDataCenter.THSData()
        size = 0
        for code in CUR_PUBLIC_NEW_STOCK:
            data = CUR_PUBLIC_NEW_STOCK[code]
            if code != cur_date:
                del (CUR_PUBLIC_NEW_STOCK[code])
                CUR_PUBLIC_NEW_STOCK[cur_date] = list(DBExec(QUERY_PATH, "FIND_PUBLIC_NEW_STOCK").execute(None))
                data = CUR_PUBLIC_NEW_STOCK[cur_date]
                size = len(data)
        logging.info(str(CUR_PUBLIC_NEW_STOCK))
        text_arr = []
        for i in range(0, size):
            d = data[i]
            if d['code'] is None:
                continue
            try:
                stock_data = center.getStockPlateInfoByCode(d['code'])
                high_end = stock_data['high_end']
                cur_price = stock_data['price']
                if cur_price != high_end:
                    text = "public volume:%s stock_code:%s,price:%s ,zf:%s ,type:%s high_count:%s" % (
                        d['public_volume'], d['code'], stock_data['price'], stock_data['growth'], d['type'],
                        d['high_count'])
                    logging.info(text)
                    text_arr.append(text)
                    d['code'] = None
            except Exception, e:
                logging.error("%s" % e)
        if len(text_arr) > 0:
            logging.info(str(text_arr))
            EmailSend.send_txt(str(text_arr), 'PUBLIC STOCK')
        pass

    def checkStopStockCode(self):
        stop_list = list(DBExec(QUERY_PATH, "FIND_STOP_STOCK").execute(None))
        center = THSDataCenter.THSData()
        # 获取当前上证指数 当前中小板指数
        sh = center.getStockPlateInfoByCode('1A0001')
        sz = center.getStockPlateInfoByCode('399001')
        z_cache = {}
        type_code = {'zxb': '399001', 'sh': '1A0001'}
        result = []
        for i in range(0, len(stop_list)):
            code = stop_list[i]['code']
            type = stop_list[i]['type']
            stock_data = center.getStockPlateInfoByCode(code)
            if stock_data:
                data = center.getStockHistoryData(code, 'last', '01')['data']
                if data:
                    arr = StringUtils.str_2_arr(data.split(";"))
                    last = arr[-1]
                    year = str(last[0])[0:4]
                    cur_type_data = None
                    if z_cache.has_key('%s_%s' % (type, year)) is not True:
                        year_type_data = center.getStockHistoryData(type_code[type], 'last', '01')['data']
                        z_cache['%s_%s' % (type, year)] = StringUtils.str_2_arr(year_type_data.split(";"))
                        pass
                    z_data = z_cache['%s_%s' % (type, year)]
                    for j in range(0, len(z_data)):
                        if last[0] == z_data[j][0]:
                            cur_type_data = z_data[j]
                            break

                    text = "c_stock:%s stock_code:%s,price:%s ,zf:%s ,type:%s    last_data:%s  dp_last:%s" % (
                        stock_data['c_stock'], code, stock_data['price'], stock_data['growth'], type,
                        str(last), str(cur_type_data))
                    result.append(text)
        if len(result) > 0:
            result.append(str(sh))
            result.append(str(sz))
            logging.info(str(result))
            EmailSend.send_txt(str(result), 'STOP STOCK')
        else:
            logging.info("no stop data")
        pass

    def __findLastNewStock(self):
        return list(DBExec(QUERY_PATH, "FIND_LAST_NEW_STOCK").execute(None))

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
                count = count - 1
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


if __name__ == '__main__':
    result = list(DBExec(QUERY_PATH, "FIND_LAST_NEW_STOCK").execute(None))
    print result
    # center = THSDataCenter.THSData()
    # code = "603986"
    # data = center.getStockMoneyLastgetStockMoneyLast(code)
    # h_code = 'hs_%s' % code
    # last_date = data[h_code]['date']
    # stockFile.write_stock_money_json(data, code+"_money", last_date)
    # print stockFile.get_stock_money_json(code,last_date)
    # StockService().saveAllDailyStocksLast()
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
    #
    # 603986
    # 600189
    # 603838
    # 600725
    # 600768
