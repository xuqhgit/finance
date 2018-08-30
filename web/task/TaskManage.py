# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2016/10/10
from apscheduler.schedulers.background import BackgroundScheduler
from web.busi.StockService import StockService
from web.busi.FundService import FundService
from web.dataCenter import StockData
import logging
import time
from web.utils import Holiday
import TaskService

schedudler = BackgroundScheduler(daemonic=False)


# url = "http://qt.gtimg.cn/r=0.4244364923797548q=marketStat,stdunixtime"
def getCurStockDailyData():
    if Holiday.is_trade_date():
        logging.info("开始获取当前stock daily数据")
        # StockService().saveAllDailyStocks()
        ts = TaskService.TaskService()
        ts.stock_daily()


def getCurStockLastData():
    if Holiday.is_trade_date():
        logging.info("开始获取当前stock last 数据")
        # StockService().saveAllDailyStocksLast()
        ts = TaskService.TaskService()
        ts.stock_last()


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


def updateCurStockTfp():
    if Holiday.is_trade_date():
        logging.info("开始更新 停复牌  数据")
        StockService().updat_stock_tfp()


def task_reset():
    logging.info("执行 任务重置 事件")
    ts = TaskService.TaskService()
    ts.reset_stock_event()
    ts.reset_stock_daily()
    ts.reset_stock_last()


def task_fund_stock():
    logging.info("执行 fund stock 事件")
    ts = TaskService.TaskService()
    ts.fund_stock()
    pass


def commonTask():
    # 获取当前stock daily数据
    schedudler.add_job(getCurStockDailyData, 'cron', minute='*/5', hour='16-17', day_of_week='0-4')
    # 获取当前stock last 数据
    schedudler.add_job(getCurStockLastData, 'cron', minute='*/6', hour='16-17', day_of_week='0-4')
    # 获取当前plate daily 数据
    schedudler.add_job(getCurPlateDailyData, 'cron', minute='00', hour='18', day_of_week='0-4')
    # 获取当前plate last 数据
    schedudler.add_job(getCurPlateLastData, 'cron', minute='15', hour='18', day_of_week='0-4')

    # 获取stock 停复牌数据
    schedudler.add_job(updateCurStockTfp, 'cron', minute='31', hour='9', day_of_week='0-4')

    # 任务重置
    schedudler.add_job(task_reset, 'cron', minute='25', hour='9', day_of_week='0-4')

    # schedudler.add_job(update_all_stock_event, 'cron', minute='00', hour='21')


    # schedudler.add_job(task_fund_stock, 'cron', minute='*/1', hour='15-23', day_of_week='0-6')


def start():
    commonTask()
    # 更新概念数据
    schedudler.add_job(updateStockBlock, 'cron', minute='30', hour='8', day_of_week='0-4')

    # 保存新股数据
    schedudler.add_job(saveStockNewData, 'cron', minute='45', hour='18', day_of_week='0-4')

    # 检测新股数据
    schedudler.add_job(checkPublicNewStockStatus, 'cron', minute='35', hour='9', day_of_week='0-4')

    # 检测停牌数据
    schedudler.add_job(checkStopStock, 'cron', minute='32', hour='9', day_of_week='0-4')

    # 清理股权登记last数据
    schedudler.add_job(StockData.clear_invalid_last_data, 'cron', minute='30', hour='9', day_of_week='0-4')


    schedudler.start()
