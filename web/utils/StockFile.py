# coding:utf-8

# @author:apple
# @date:16/4/29

from web.utils import FileUtils
import StringUtils

stock_file = "stock/%s/%s.json"
stock_date_file = "stock/history/%s/%s/%s/%s/%s.json"
stock_year_file = "stock/history/year/%s/%s/%s.json"


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
        return StringUtils.str_2_json(FileUtils.get_static_file(stock_file % ('newStock', 'data.json')))

    @staticmethod
    def write_new_stock_json(data):
        """
        写入最近新股数据
        :param data:
        :return:
        """
        FileUtils.write_static_data(stock_file % ('newStock', 'data.json'), StringUtils.json_2_str(data))

    @staticmethod
    def write_stock_json(data, code, date):
        """
        写入日期数据
        :param data:
        :param code:
        :param date:
        :return:
        """
        code_type = StringUtils.stock_code_type(code)
        if type:
            FileUtils.write_static_data(stock_date_file % (code_type, date[0:4], date[4:6], date[6:8], code),
                                        StringUtils.json_2_str(data))
        pass

    @staticmethod
    def get_stock_json(code, date):
        """
        获取stock 日期数据
        :param code:
        :param date:
        :return:
        """
        code_type = StringUtils.stock_code_type(code)
        if code_type:
            stock_str = FileUtils.get_static_file(stock_date_file % (code_type, date[0:4], date[4:6], date[6:8], code))
            return StringUtils.str_2_json(stock_str)

    @staticmethod
    def write_stock_money_json(data, code, date):
        """
        写入日期数据
        :param data:
        :param code:
        :param date:
        :return:
        """
        code_type = StringUtils.stock_code_type(code)
        if type:
            FileUtils.write_static_data(stock_date_file % (code_type, date[0:4], date[4:6], date[6:8], code + "_money"),
                                        StringUtils.json_2_str(data))
        pass

    @staticmethod
    def get_stock_money_json(code, date):
        """
        获取stock 日期数据
        :param code:
        :param date:
        :return:
        """
        code_type = StringUtils.stock_code_type(code)
        if code_type:
            stock_str = FileUtils.get_static_file(
                stock_date_file % (code_type, date[0:4], date[4:6], date[6:], code + "_money"))
            return StringUtils.str_2_json(stock_str)

    @staticmethod
    def get_stock_year_type_json(code, year, code_type):
        """
        获取指定年份和类型的数据
        :param code:
        :param year:
        :param code_type:
        :return:
        """
        stock_str = FileUtils.get_static_file(stock_year_file % (year, code_type, code))
        return StringUtils.str_2_json(stock_str)

    @staticmethod
    def del_stock_year_type_json(code, year, code_type):
        """
        删除指定年份和类型的数据
        :param code:
        :param year:
        :param code_type:
        :return:
        """
        FileUtils.del_static_file(stock_year_file % (year, code_type, code))

    @staticmethod
    def save_stock_year_type_json(data, code, year, code_type):
        """
        保存指定年份和类型的数据
        :param data:
        :param code:
        :param year:
        :param code_type:
        :return:
        """
        FileUtils.write_static_data(stock_year_file % (year, code_type, code), StringUtils.json_2_str(data))
