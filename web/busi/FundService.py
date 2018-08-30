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
        # company_list = [{"id":"80000111","code":"80175498"}]
        for c in company_list:
            try:
                fund_list = FundData.get_fund_list_by_company(c['id'], c['code'])
                if bool(fund_list):
                    result = []
                    code_list = db.setId("GET_FUND").execute({'code_list':fund_list})
                    code_list_h = [i['code'] for i in code_list]
                    for i in range(0,len(fund_list)):
                        if fund_list[i]['code'] not in code_list_h:
                            result.append(fund_list[i])
                    if bool(result):
                        db.setId("SAVE_FUND").execute(result)
                        DBExec(Query.QUERY_FINANCE_TASK, "")
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

    def get_stock_fund(self, stock_code, end_date=''):
        """
        根据股票代码获取基金
        :param stock_code:
        :return:
        """
        end_date = '2018-06-31'
        db = DBExec(Query.QUERY_FUND, "GET_FUND_STOCK")
        fund_list = db.execute({"stock_code": stock_code, "end_date": end_date})
        result = []
        if bool(fund_list):
            code_len = len(fund_list)
            CommonUtils.start_many_thread(fund_list,
                                          handleSize=int(code_len / (code_len > 3 and 3 or code_len)),
                                          args=(result,),
                                          target=self.__get_fund_info,
                                          asyn=False, name='获取FUND INFO')
        return fund_list

    def __get_fund_info(self, fund_list, result):
        """
        根据fund 列表获取 信息
        :param fund_list:
        :param result:
        :return:
        """
        for f in fund_list:
            f['scale'] = float(f['scale'])
            f['quantity'] = float(f['quantity'])
            res = FundData.get_fund_daily(f['fund_code'])
            if res:

                f.update(res)


if __name__ == '__main__':
    print FundService().save_fund()
    pass
