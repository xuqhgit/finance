# coding:utf-8


class StockData(object):
    def __init__(self):
        pass

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
        pass

    def getAllStockConcept(self):
        """
        获取所有股票概念信息
        :return:
        """
        pass

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
        """
        获取指定股票5分数据
        :param code:
        :return:
        """
        pass

    def getStockConceptByCode(self):
        """
        通过股票代码获取相应的股票概念数据
        :return:
        """
        pass

    def getStockPlateInfoByCode(self):
        """
        通过股票代码获取股票相应的盘口数据
        :return:
        """
        pass

    def getStockLast(self, code):
        """
        获取股票最后交易数据
        :return:
        """
        pass

    def getStockMoneyLast(self, code):
        """
        获取股票最后资金数据
        :param code:
        :return:
        """
        pass

    def getBondDailyByCode(self, code):
        """
        获取债券日数据
        :param code:
        :return:
        """
        pass

    def getBondLastByCode(self, code):
        """
        获取债券日交易数据
        :param code:
        :return:
        """
        pass

    def getFundDailyByCode(self, code):
        """
        获取基金日数据
        :param code:
        :return:
        """
        pass

    def getFundLastByCode(self, code):
        """
        获取基金日交易数据
        :param code:
        :return:
        """
        pass

    def getStockPlateDailyByCode(self, code):
        """
        获取股票版块daily数据 包含 行业 区域 概念
        :return:
        """
        pass

    def getPlateLast(self, code):
        """
        获取板块最后交易数据
        :return:
        """
        pass
