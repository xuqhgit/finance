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


def get_fund_company(data_type=""):
    """
    获取基金公司数据
    :param data_type:
    :return:
    """
    return eastmoneyData.get_fund_company()


def get_fund_list_by_company(company_id, company_code):
    result = eastmoneyData.get_fund_list_by_company(company_code)
    if bool(result):
        for f in result:
            f['company_id'] = company_id
    else:
        logging.error("获取公司[%s][%s]基金数据异常" % (company_id, company_code))
    return result


def get_fund_stock(fund_code):
    """
    获取基金股票信息
    :param fund_code:
    :return:
    """
    month = (int(Holiday.get_cur_month()) - 1) / 3
    month = month == 0 and 12 or month * 3
    try:
        return eastmoneyData.get_fund_stock(fund_code, month)
    except Exception, e:
        print e
        logging.error("获取基金[%s] 持股数据异常:%s" % (fund_code, e.message))
    return None


if __name__ == '__main__':
    print get_fund_stock("003096")
