# coding:utf-8

# @author:apple
# @date:16/4/29

from web.utils import FileUtils
from StringUtils import StringUtils
from web.dataCenter.THSDataCenter import THSData


stock_file = "stock/%s/%s.json"
stock_date_file = "stock/%s/%s/%s.json"


class StockFile(object):
    """

    """

    def __init__(self):
        pass

    @staticmethod
    def get_new_stock_json():
        """
        获取最近新股数据
        :return:
        """
        return StringUtils.str_2_json(FileUtils.get_file(stock_file % ('newStock', 'data.json')))

    @staticmethod
    def write_new_stock_json(data):
        """
        写入最近新股数据
        :param data:
        :return:
        """
        FileUtils.write_data(stock_file % ('newStock', 'data.json'), StringUtils.json_2_str(data))

    @staticmethod
    def write_stock_json(data, code, date):
        """
        写入日期数据
        :param data:
        :param code:
        :param date:
        :return:
        """
        code_type = StringUtils.stock_code_type()
        if type:
            FileUtils.write_data(stock_date_file % (code_type, date, code + '.json'), StringUtils.json_2_str(data))
        pass

    @staticmethod
    def get_stock_json(code, date):
        """
        获取stock 日期数据
        :param code:
        :param date:
        :return:
        """
        code_type = StringUtils.stock_code_type()
        if code_type:
            return StringUtils.str_2_json(stock_date_file % (code_type, date, code + '.json'))


if __name__ == '__main__':
    d = THSData()
    i=0
    while i<5:
        i=i+1
        str = d.getPlateLast('603848')
        print str





