# coding:utf-8


import THSDataCenter
from web.utils import StringUtils
from web.utils import CommonUtils
from web.utils import Holiday
import logging

import json
from web.utils.StockFile import StockFile

"""
根据业务获取数据
"""
thsDataCenter = THSDataCenter.THSData()
stockFile = StockFile()


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
        p_json = thsDataCenter.getStockPlateInfoByCode(code)
        if p_json:
            # 时间,开,高,低,收,成交量,成交额,换手
            old_data.append([int(Holiday.get_cur_date()), p_json['open_price'], p_json['high_price'],
                             p_json['low_price'], p_json['price'], p_json['volume_transaction'],
                             p_json['turnover'], p_json['turnover_rate']])
        return old_data
    return None


def refresh_stock_last_day(thsDataList):
    """
    刷新日交易数据
    :param thsDataList:
    :return:
    """
    try:
        CommonUtils.start_many_thread(thsDataList, handleSize=300, target=__save_stock_last_day)
    except Exception, e:
        logging.error("刷新日交易数据 -->异常")
        logging.error(e)
    pass


def __save_stock_last_day(ths_data_list,result):
    """

    :return:
    """
    for i in range(len(ths_data_list)):
        year = "last"
        d_type = "01"
        ths_data = ths_data_list[i]
        code = ths_data['stock_code']
        try:
            old_data = stockFile.get_stock_year_type_json(code, year, d_type)
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


if __name__ == "__main__":
    p_json = thsDataCenter.getStockPlateInfoByCode("002606")
    p_json1 = thsDataCenter.getStockPlateInfoByCode("603300")
    p_json2 = thsDataCenter.getStockPlateInfoByCode("600547")
    refresh_stock_last_day([p_json,p_json1,p_json2])
