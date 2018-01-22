# coding:utf-8

from web.db.dbexec import DBExec
from web.db import Query


def insert(data):
    DBExec(Query.QUERY_HANDLE_LOG, "INSERT_HANDLE_LOG").execute(data)
