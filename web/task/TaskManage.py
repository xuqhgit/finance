# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2016/10/10
from apscheduler.schedulers.background import BackgroundScheduler
from web.busi.StockService import StockService
from web.busi.StockEventService import StockEventService
from web.dataCenter import StockData
import logging
import time
from web.utils import Holiday

schedudler = BackgroundScheduler(daemonic=False)


# url = "http://qt.gtimg.cn/r=0.4244364923797548q=marketStat,stdunixtime"
def getCurStockDailyData():
    if Holiday.is_trade_date():
        logging.info("开始获取当前stock daily数据")
        StockService().saveAllDailyStocks()


def getCurStockLastData():
    if Holiday.is_trade_date():
        logging.info("开始获取当前stock last 数据")
        StockService().saveAllDailyStocksLast()


def getCurPlateDailyData():
    if Holiday.is_trade_date():
        logging.info("开始当前plate daily 数据")
        StockService().saveAllDailyPlate()


def getCurPlateLastData():
    if Holiday.get_cur_date():
        logging.info("开始获取当前plate last 数据")
        StockService().saveAllDailyPlateLast()


def saveStockNewData():
    if Holiday.is_trade_date():
        logging.info("开始保存当前new stock 数据")
        StockService().saveStockNew()


def updateStockBlock():
    if Holiday.is_trade_date():
        logging.info("开始更新stock block 数据")
        StockService().saveStockBlockData()


def checkStopStock():
    if Holiday.is_trade_date():
        logging.info("开始检查 stop stock  数据")
        StockService().checkStopStockCode()


def checkPublicNewStockStatus():
    if Holiday.is_trade_date():
        cur_time = time.strftime('%H%M', time.localtime(time.time()))
        cur_time = int(cur_time)
        if 930 <= cur_time < 1130 or 1300 < cur_time < 1500:
            logging.info("开始检测 public new stock status")
            StockService().checkPublicNewStockStatus()


def update_all_stock_event():
    # if Holiday.get_cur_date():
    logging.info("开始获取 stock event  数据")
    StockEventService().update_all_stock_event()


def commonTask():
    # 获取当前stock daily数据
    schedudler.add_job(getCurStockDailyData, 'cron', minute='10', hour='15', day_of_week='0-4')
    # 获取当前stock last 数据
    schedudler.add_job(getCurStockLastData, 'cron', minute='30', hour='16', day_of_week='0-4')
    # 获取当前plate daily 数据
    schedudler.add_job(getCurPlateDailyData, 'cron', minute='00', hour='16', day_of_week='0-4')
    # 获取当前plate last 数据
    schedudler.add_job(getCurPlateLastData, 'cron', minute='15', hour='16', day_of_week='0-4')

    # 更新事件
    schedudler.add_job(update_all_stock_event, 'cron', minute='00', hour='9', day_of_week='0-4')
    schedudler.add_job(update_all_stock_event, 'cron', minute='00', hour='21')


def start():
    commonTask()
    # 更新概念数据
    schedudler.add_job(updateStockBlock, 'cron', minute='00', hour='8', day_of_week='0-4')

    # 保存新股数据
    schedudler.add_job(saveStockNewData, 'cron', minute='00', hour='18', day_of_week='0-4')

    # 检测新股数据
    schedudler.add_job(checkPublicNewStockStatus, 'cron', minute='*/5', hour='9-11', day_of_week='0-4')

    # 检测停牌数据
    schedudler.add_job(checkStopStock, 'cron', minute='32', hour='9', day_of_week='0-4')

    # 清理股权登记last数据
    schedudler.add_job(StockData.clear_invalid_last_data, 'cron', minute='30', hour='9', day_of_week='0-4')

    schedudler.start()

