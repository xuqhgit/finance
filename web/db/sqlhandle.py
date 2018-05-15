# coding:utf-8

import os
import re
import logging
from jinja2 import Template
import web
from web.utils.xmlutils import XmlUtils


class SqlHandle(object):
    """sql 处理类"""

    def __init__(self):
        pass

    @staticmethod
    def get_sql(tmplUrl, id, param):
        """
        :param tmplUrl: 模板的路径
        :param id: 获取ele的id
        :param param: 参数dict
        :return:
        """
        if param is None:
            param={}
        if tmplUrl is None or tmplUrl == '':
            return -1, "未获取到sql-模板路径", None
        if id is None or id == '':
            return -1, '未获取到id', None
        path = os.path.join(web.web_dir, 'templates/query/%s.xml' % tmplUrl)
        element = XmlUtils(path).getElementById(id, "query")
        sql_tmpl = None
        if element:
            sqlNode = element.getElementsByTagName('sql')
            if sqlNode is None:
                return -1, "配置文件格式错误[sql]未被定义", None
            sql_tmpl = sqlNode[0].firstChild.wholeText
            if sql_tmpl is None or sql_tmpl == '':
                return -1, "未获取到sql语句", None

            sql = Template(sql_tmpl).render(type(param) == list and {"list":param} or param)
            sql, arr = SqlHandle.sql_regex_handle(sql)
            return 0, sql and sql.strip().replace("\r", " ").replace("\t"," ") or None,\
                   arr and arr or None, element.getAttribute('type')
        logging.error("获取sql异常：%s ---> %s" % (tmplUrl, id))
        return -1, None, None, None

    @staticmethod
    def sql_regex_handle(sql):
        """
        去掉sql中的[] 替换成%s
        :param sql: 需要处理的sql
        :return: 返回处理的sql,并且返回替换的[xxx][xx] 中的xxx数组
        """
        arr = re.findall(r'(?<=\[).*?(?=\])', sql)
        result, num = re.subn(r'\[.*?\]', '%s', sql)
        result, num = re.subn(r'\?', '%s', result)
        if arr and len(arr) > 0:
            for i in range(len(arr)):
                arr[i] = arr[i].strip()
        return result, arr


if __name__ == '__main__':
    template = Template('Hello {{ name }}!')
    param = {'name': 'json'}
    print template.render(param)
