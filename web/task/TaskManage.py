# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2016/10/10
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from web.busi.StockService import StockService
import logging
import time

schedudler = BackgroundScheduler(daemonic=False)


# url = "http://qt.gtimg.cn/r=0.4244364923797548q=marketStat,stdunixtime"
def getCurStockDailyData():
    logging.info("开始获取当前stock daily数据")
    StockService().saveAllDailyStocks()


def getCurStockLastData():
    logging.info("开始获取当前stock last 数据")
    StockService().saveAllDailyStocksLast()


def getCurPlateDailyData():
    logging.info("开始当前plate daily 数据")
    StockService().saveAllDailyPlate()


def getCurPlateLastData():
    logging.info("开始获取当前plate last 数据")
    StockService().saveAllDailyPlateLast()


def saveStockNewData():
    logging.info("开始保存当前new stock 数据")
    StockService().saveStockNew()


def updateStockBlock():
    logging.info("开始更新stock block 数据")
    StockService().saveStockBlockData()


def checkStopStock():
    logging.info("开始检查 stop stock  数据")
    StockService().checkStopStockCode()


def checkPublicNewStockStatus():
    logging.info("开始检测 public new stock status")
    s_a = 930
    s_b = 1000
    cur_time = time.strftime('%H%M', time.localtime(time.time()))
    cur_time = int(cur_time)
    if (cur_time > s_a and cur_time < s_b):
        StockService().checkPublicNewStockStatus()


def commonTask():
    # 获取当前stock daily数据
    schedudler.add_job(getCurStockDailyData, 'cron', minute='42', hour='17', day_of_week='0-4')
    # 获取当前stock last 数据
    # schedudler.add_job(getCurStockLastData, 'cron', minute='25', hour='15', day_of_week='0-4')
    # 获取当前plate daily 数据
    schedudler.add_job(getCurPlateDailyData, 'cron', minute='10', hour='16', day_of_week='0-4')
    # 获取当前plate last 数据
    # schedudler.add_job(getCurPlateLastData, 'cron', minute='45', hour='15', day_of_week='0-4')


def start():
    commonTask()
    # 更新概念数据
    schedudler.add_job(updateStockBlock, 'cron', minute='00', hour='8', day_of_week='0-4')

    # 保存新股数据
    schedudler.add_job(saveStockNewData, 'cron', minute='30', hour='16', day_of_week='0-4')

    # 保存新股数据
    schedudler.add_job(checkPublicNewStockStatus, 'cron', minute='*/1', hour='9-11', day_of_week='0-4')


    # 检测停牌数据
    schedudler.add_job(checkStopStock, 'cron', minute='32', hour='9', day_of_week='0-4')




    schedudler.start()
