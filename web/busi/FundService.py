# coding:utf-8


from web.db.dbexec import DBExec
from web.db import Query
from web.utils.webclient import WebClient
from web.utils import CommonUtils
from web.dataCenter import FundData
import thread
from threading import Thread
import json
import time
import logging


class FundService(object):
    def __init__(self):
        pass

    def save_fund_company(self):
        """
        保存所有基金公司信息
        :return:
        """
        result = FundData.get_fund_company()
        if bool(result):
            res = DBExec(Query.QUERY_FUND, "SAVE_FUND_COMPANY").execute(result)
            logging.info("保存基金公司数据:%s" % res)
            return res

    def save_fund(self):
        """
        保存公司基金数据
        :return:
        """
        db = DBExec(Query.QUERY_FUND, "")
        company_list = db.setId("GET_FUND_COMPANY").execute(None)
        for c in company_list:
            try:
                fund_list = FundData.get_fund_list_by_company(c['id'], c['code'])
                if bool(fund_list):
                    db.setId("SAVE_FUND").execute(fund_list)
            except Exception, e:
                print e
                logging.error("保存基金数据错误【%s】：%s" % (json.dumps(c), e.message))

    def save_fund_stock(self, fund_code_list):
        if bool(fund_code_list) is False:
            return
        db = DBExec(Query.QUERY_FUND, "")
        code_len = len(fund_code_list)
        result = []
        CommonUtils.start_many_thread(fund_code_list, handleSize=int(code_len / (code_len > 5 and 5 or code_len)),
                                      args=(result,),
                                      target=self.__save_fund_stock,
                                      asyn=False, name='获取FUND STOCK ')
        # print result
        # db.setId("SAVE_FUND_STOCK").execute(result)

    def __save_fund_stock(self, fundList, result):
        db = DBExec(Query.QUERY_FUND, "")
        res = []
        for f in fundList:
            s = FundData.get_fund_stock(f['code'])
            if s:
                res.extend(s)
        # result.extend(res)
        db.setId("SAVE_FUND_STOCK").execute(res)
        db.commitTrans()


if __name__ == '__main__':
    FundService().save_fund()
    pass
