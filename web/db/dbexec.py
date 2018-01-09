# coding:utf-8
# @author:apple
# @date:16/1/24

from sqlhandle import SqlHandle
import re
from web.db import db
import logging


# def transaction(closeConn=True):
#     def innerTrans(func):
#         @functools.wraps(func)
#         def inner(*args, **kvargs):
#             if hasattr(LOCAL_THREAD, "TRAN_COUNT") is False:
#                 LOCAL_THREAD.TRAN_COUNT = 0
#             LOCAL_THREAD.TRAN_COUNT += 1
#             try:
#                 func(*args, **kvargs)
#                 if LOCAL_THREAD.TRAN_COUNT > 0:
#                     LOCAL_THREAD.TRAN_COUNT -= 1
#                 logging.debug("tran_count:%s" % LOCAL_THREAD.TRAN_COUNT)
#                 if LOCAL_THREAD.TRAN_COUNT == 0:
#                     logging.info("提交事务")
#                     LOCAL_THREAD.DB.commit()
#                     if closeConn:
#                         LOCAL_THREAD.DB.dispose()
#             except Exception, e:
#                 logging.error(e)
#                 if hasattr(LOCAL_THREAD, "DB") and LOCAL_THREAD.DB:
#                     logging.error("出现异常事务回滚[COUNT:%s]" % LOCAL_THREAD.TRAN_COUNT)
#                     LOCAL_THREAD.DB.rollback()
#                     logging.error("释放数据库连接")
#                     LOCAL_THREAD.DB.dispose()
#                     LOCAL_THREAD.DB = None
#                 LOCAL_THREAD.TRAN_COUNT = 0
#                 raise Exception, e
#
#         return inner
#
#     return innerTrans



class DBExec(object):
    """
        db执行器
    """

    def __init__(self, tmplUrl, id):

        self.tmplUrl = tmplUrl
        self.id = id
        self.db = db.Mysql()

    def set(self, tmplUrl, id):
        self.tmplUrl = tmplUrl
        self.id = id
        return self

    def setId(self, id):
        self.id = id
        return self

    def setTmplUrl(self, tmplUrl):
        self.tmplUrl = tmplUrl
        return self

    def execute(self, data, print_param=False, print_sql=True, **sqlParam):

        status, sql_str, arr = SqlHandle.get_sql(self.tmplUrl, self.id, **sqlParam)
        if status == 0:
            sql = sql_str.strip()
            if print_sql:
                logging.info(sql)
                logging.info(arr)
            flag = re.match(r'select', sql, re.I)
            _data = []
            if arr and data:
                if type(data) == list:
                    for d in data:
                        _d = []
                        for a in arr:
                            if a in d:
                                # if type(d[a]) == unicode:
                                #     _d.append(d[a].decode('unicode_escape'))
                                # else:
                                #     _d.append(d[a])
                                _d.append(d[a])
                            else:
                                _d.append('')
                        _data.append(_d)
                else:
                    for a in arr:
                        if a in data:
                            # if type(data[a]) == unicode:
                            #     _data.append(data[a].decode('unicode_escape'))
                            # else:
                            #     _data.append(data[a])
                            _data.append(data[a])
                        else:
                            _data.append('')
                if print_param:
                    logging.info(_data)
            if len(_data) is 0:
                _data = None
            if flag:
                page = 0
                pageSize = 12
                if data and "page" in data and int(data["page"]) > 0:
                    page = int(data["page"])
                    if "pageSize" in data and int(data["pageSize"]) > 0:
                        pageSize = int(data["pageSize"])
                return self.__query(sql, _data, page=page, pageSize=pageSize)
            else:
                if type(data) == list:
                    return self.__saveDetch(sql, _data)
                else:
                    return self.__save(sql, _data)

        else:
            logging.info(str)
        return None

    def setParams(self, tmpUrl=None, id=None):
        if tmpUrl:
            self.tmplUrl = tmpUrl
        if id:
            self.id = id
        return self

    def startTrans(self):
        self.trans = True
        return self

    def commitTrans(self):
        self.db.commit()
        return self

    def rollBackTrans(self):
        self.db.rollback()
        return self

    def __save(self, sql, param):
        """
        执行update,insert,delete语句
        :param sql:
        :param param:
        :return:
        """
        count = self.db.saveOne(sql, param)
        return count

    def __saveDetch(self, sql, param):
        """
        执行update,insert,delete语句
        :param sql:
        :param param:
        :return:
        """
        count = self.db.saveMany(sql, param)
        return count

    def __query(self, sql, param, page=0, pageSize=13):
        """

        :param sql: 执行sql
        :param param: sql参数
        :param page: 分页数
        :param pageSize: 分页数据大小
        :return:
        """
        if page > 0:
            _sql = 'select count(*) as total from (%s) as sc' % sql

            result = self.db.getOne(_sql, param)
            total = result['total']

            pageFrom = (page - 1) * pageSize
            pageSum = (total - 1) / pageSize + 1
            sql = "select * from (%s) as fy limit %d,%d" % (sql, pageFrom, pageSize)
            logging.info(sql)

            res = self.db.getAll(sql)
            if res is None:
                res = []
            return {"total": total, "pageSum": pageSum, "curPage": page, "pageSize": pageSize, "rows": res}
        result = self.db.getAll(sql, param)
        if result and len(result) == 1:
            return result[0]
        else:
            return result
