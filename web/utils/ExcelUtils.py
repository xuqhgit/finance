# coding:utf-8

# @author:apple
# @date:16/4/3

import xlrd


class ExcelUtils(object):
    """
        字符串工具类
    """

    def __init__(self):
        pass

    @staticmethod
    def getExcelData(filePath, fromRow = 0):
        list = []
        try:
            print '读取:%s 文件中....' % (filePath)
            data = xlrd.open_workbook(u'%s' % filePath)
            table = data.sheet_by_name('sheet 1')
            nrows = table.nrows  # 行数
            colnames = table.row_values(fromRow)  # 某一行数据
            for rownum in range(fromRow, nrows):
                row = table.row_values(rownum)
                if row:
                    app = {}
                    for i in range(len(colnames)):
                        app[i] = row[i]
                    list.append(app)
        except Exception, e:
            print str(e)
            return None

        return list




if __name__ == '__main__':
    pass

