# -*- coding: UTF-8 -*-
"""
desc:数据库操作类
@note:
1、执行带参数的ＳＱＬ时，请先用sql语句指定需要输入的条件列表，然后再用tuple/list进行条件批配
２、在格式ＳＱＬ中不需要使用引号指定数据类型，系统会根据输入参数自动识别
３、在输入的值中不需要使用转意函数，系统会自动处理
"""

# import MySQLdb
# from MySQLdb.cursors import DictCursor
import mysql.connector as connor

from DBUtils.PooledDB import PooledDB
from web.utils import ConfigUtils


Config = {
    'host': ConfigUtils.get("mysql", "host"),
    'port': int(ConfigUtils.get("mysql", "port")),
    'user': ConfigUtils.get("mysql", "name"),
    'passwd': ConfigUtils.get("mysql", "password"),
    'charset': 'utf8',
    'db': ConfigUtils.get("mysql", "db")
}
"""
    mincached : 启动时开启的闲置连接数量(缺省值 0 以为着开始时不创建连接)
    maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
    maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
    maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
    blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,连接被分配)
    maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
    setsession : 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]

"""

"""
Config是一些数据库的配置文件
"""


class Mysql(object):
    """
        MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
        获取连接对象：conn = Mysql.getConn()
        释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self):
        """
        数据库构造函数，从连接池中取出连接，并生成操作游标
        """
        self._conn = Mysql.__getConn()
        self._cursor = self._conn.cursor(dictionary=True)

    @staticmethod
    def __getConn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """

        if Mysql.__pool is None:
            __pool = PooledDB(creator=connor, maxshared=0, **Config)
        return __pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        # if count > 0:
        #     result = self._cursor.fetchall()
        # else:
        #     result = None
        result = self._cursor.fetchall()
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        # if count > 0:
        #     result = self._cursor.fetchone()
        # else:
        #     result = None
        result = self._cursor.fetchone()
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        # if count > 0:
        #     result = self._cursor.fetchmany(num)
        # else:
        #     result = None
        result = self._cursor.fetchmany(num)
        return result

    def insertOne(self, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        try:
            self._cursor.execute(sql, value)
        except Exception, e:
            raise Exception(e)
        return self.__getInsertId()

    def saveOne(self, sql, value, type=0):
        """

        :param sql: 执行的sql语句
        :param value: 值
        :param type: 0为insert 1为update 2 delete
        :return: 如果type为0则返回插入后的id 否则返回影响数据的数量count

        """

        try:
            count = self._cursor.execute(sql, value)
        except Exception, e:
            self.rollback()
            raise Exception(e)
        if type == 0:
            return self.__getInsertId()
        else:
            return self._cursor.rowcount

    def saveMany(self, sql, values):
        """
        @summary: 向数据表保存多条记录
        @param sql:要保存的ＳＱＬ格式
        @param values:要保存的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        try:
            count = self._cursor.executemany(sql, values)
        except Exception, e:
            self.rollback()
            raise Exception(e)
        return self._cursor.rowcount

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def startTrans(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def commit(self):
        """
        @summary: 提交事务
        """
        self._conn.commit()

    def rollback(self):
        """
        @summary: 回滚事务
        """
        self._conn.rollback()

    def dispose(self):
        """
        @summary: 释放连接池资源
        """
        self._cursor.close()
        self._conn.close()
