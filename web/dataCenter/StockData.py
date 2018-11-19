# coding:utf-8


import THSDataCenter
from web.utils import StringUtils
from web.utils import CommonUtils
from web.utils import Holiday
import logging
from web.db import Query
from web.db.dbexec import DBExec

from web.utils.StockFile import StockFile

import BaiduDataCenter
import EastmoneyDataCenter
import HexunDataCenter
import JRJDataCenter
import SohuDataCenter
import SsajaxDataCenter
import TCDataCenter
import XgbDataCenter

"""
根据业务获取数据
"""
thsDataCenter = THSDataCenter.THSData()
stockFile = StockFile()

baiduData = BaiduDataCenter.BaiduData()
eastmoneyData = EastmoneyDataCenter.EastmoneyData()
hexunData = HexunDataCenter.HexunData()
jrjData = JRJDataCenter.JRJData()
sohuData = SohuDataCenter.SohuData()
ssajaxData = SsajaxDataCenter.SsajaxData()
tcData = TCDataCenter.TCData()
xgbData = XgbDataCenter.XgbData()


def get_stock_last_day(code):
    """
    获取stock的日数据
    :param code:
    :return:
    """
    year = "last"
    d_type = "01"
    old_data = stockFile.get_stock_year_type_json(code, year, d_type)
    if old_data is None:
        # 目前从THS 获取
        data = thsDataCenter.getStockHistoryData(code, year, d_type)
        if data is None:
            return None
        old_data = StringUtils.handle_ths_str_data_to_list(data['data'])
        stockFile.save_stock_year_type_json(old_data, code, year, d_type)
    # 交易日
    if Holiday.is_trade_date() is False:
        return old_data
    if Holiday.is_trade_time():
        p_json = get_stock_cur_trade(code)
        if p_json and p_json['open_price'] != 0:
            # 时间,开,高,低,收,成交量,成交额,换手
            old_data.append([int(Holiday.get_cur_date()), p_json['open_price'], p_json['high_price'],
                             p_json['low_price'], p_json['price'], p_json['volume_transaction'],
                             0, p_json['turnover_rate']])
    return old_data


def refresh_stock_last_day(thsDataList):
    """
    刷新日交易数据
    :param thsDataList:
    :return:
    """
    try:
        CommonUtils.start_many_thread(thsDataList, handleSize=300, target=__save_stock_last_data,
                                      name='日交易数据刷新任务')
    except Exception, e:
        logging.error("刷新日交易数据 -->异常")
        logging.error(e)
    pass


def __save_stock_last_data(ths_data_list):
    """
    保存stock 交易数据
    :return:
    """
    for i in range(len(ths_data_list)):
        year = "last"
        d_type = "01"
        ths_data = ths_data_list[i]
        code = ths_data['stock_code']
        if ths_data['trade_stop'] != 0:
            logging.info("刷新--保存--日交易数据 -->获取日数据 停牌：%s" % code)
            continue
        try:
            old_data = stockFile.get_stock_year_type_json(code, year, d_type)
            if ths_data['name'].find('XD') != -1:
                old_data = None
                logging.info("刷新--保存--日交易数据 -->获取日数据 除息：%s" % code)
            if ths_data['name'].find('XR') != -1:
                old_data = None
                logging.info("刷新--保存--日交易数据 -->获取日数据 除权：%s" % code)
            if old_data is None:
                # 目前从THS 获取
                data = thsDataCenter.getStockHistoryData(code, year, d_type)
                if data is None:
                    logging.error("刷新--保存--日交易数据 -->获取日数据失败：%s" % code)
                    continue
                old_data = StringUtils.handle_ths_str_data_to_list(data['data'])
            p_json = ths_data
            if len(old_data) == 0 or int(old_data[len(old_data) - 1][0]) != Holiday.get_cur_date():
                # 时间,开,高,低,收,成交量,成交额,换手
                old_data.append([int(Holiday.get_cur_date()), p_json['open_price'], p_json['high_price'],
                                 p_json['low_price'], p_json['price'], p_json['volume_transaction'],
                                 p_json['turnover'], p_json['turnover_rate']])
            stockFile.save_stock_year_type_json(old_data, code, year, d_type)
        except Exception, e:
            logging.error("刷新--保存--日交易数据 -->异常：%s" % code)
            logging.error(e)


def clear_invalid_last_data():
    year = "last"
    d_type = "01"
    stock_list = DBExec(Query.QUERY_STOCK, "GET_CUR_DJ_STOCK").execute(None)
    if isinstance(stock_list, dict):
        stock_list = [stock_list]
    for s in stock_list:
        logging.info("股权登记--清理--日交易数据 -->code：%s" % s['code'])
        stockFile.del_stock_year_type_json(s['code'], year, d_type)
    pass


def get_stock_cur_last(code, date=None):
    """
    获取stock 当前的最后交易数据
    :param code:
    :param date:
    :return:
    """
    cur_date = Holiday.get_cur_date()
    stock_json = None
    if date is None:
        date = cur_date
    if date == cur_date and Holiday.is_trade_date_time():
        stock_json = thsDataCenter.getStockLast(code)
    if stock_json is None:
        stock_json = stockFile.get_stock_json(code, date)
    if date == cur_date:
        stock_json = thsDataCenter.getStockLast(code)
    if stock_json:
        stock_json = stock_json["hs_%s" % code]
        stock_json['data'] = StringUtils.handle_ths_str_data_to_list(stock_json['data'])
        return stock_json
    return None


def get_stock_cur_trade(code, count=8, index=None):
    """
    获取当前信息
    :param code:
    :return:
    """

    if code == '1A0001' or code == '399001':
        return None
    try:
        code_int = (index is None and int(code) or index) + count
    except Exception, e:
        return get_stock_cur_trade(code, index=1)
    try:
        result = None
        if code_int % 8 == 0:
            result = baiduData.getCurData([code])[0]
        elif code_int % 8 == 1:
            result = eastmoneyData.getCurData(code)
        elif code_int % 8 == 2:
            result = hexunData.getCurData([code])[0]
        elif code_int % 8 == 3:
            result = jrjData.getCurData([code])[0]
        elif code_int % 8 == 4:
            result = sohuData.getCurData(code)
        elif code_int % 8 == 5 and count == 8:
            result = ssajaxData.getCurData(code)
        elif code_int % 8 == 6:
            result = tcData.getCurData(code)
        elif code_int % 8 == 7:
            result = xgbData.getCurData([code])[0]
    except Exception, e:
        logging.error("获取Stock当前信息错误：%s-->%s" % (code_int % 8, e))
    if count == 0:
        return result
    if result is None:
        return get_stock_cur_trade(code, count=count - 1, index=index)
    return result


def get_cur_stock_tfp(**params):
    """
    获取当前停复牌
    :param params:
    :return:
    """
    try:
        result = eastmoneyData.get_stock_tfp(**params)
        return result
    except Exception, e:
        logging.error("获取Stock当前停复牌信息错误：%s" % (e))
    return None


def get_stock_history_lift(code):
    """
    获取stock历史解禁数据
    :param code:
    :return:
    """
    try:
        result = eastmoneyData.get_stock_history_jj_data(code)
        return result
    except Exception, e:
        logging.error("获取Stock历史解禁信息错误：%s----%s" % (code, e))
    return None

def get_stock_future_lift(start_date,end_date):
    """
    获取stock历史解禁数据
    :param start_date:
    :param end_date:
    :return:
    """
    try:
        result = eastmoneyData.get_jj_data_by_date(start_date=start_date,end_date=end_date)
        return result
    except Exception, e:
        logging.error("获取Stock历史解禁信息错误：%s:%s---%s" % (start_date,end_date, e))
    return None


def get_stock_money(code):
    """

    :param code:
    :return:
    """
    try:
        result = eastmoneyData.get_stock_money(code)
        return result
    except Exception, e:
        logging.error("获取Stock 资金流入数据错误：%s----%s" % (code, e))
    return None


if __name__ == "__main__":
    # p_json = thsDataCenter.getStockPlateInfoByCode("002606")
    # p_json['name'] = 'XD除息'
    # p_json1 = thsDataCenter.getStockPlateInfoByCode("603300")
    # p_json2 = thsDataCenter.getStockPlateInfoByCode("600547")
    # refresh_stock_last_day([p_json, p_json1, p_json2])
    # data = get_stock_cur_last("603506")
    # clear_invalid_last_data()
    # print data
    a = {}
    print a['a']
    pass
