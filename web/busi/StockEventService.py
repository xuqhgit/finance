# coding:utf-8
from web.utils import EmailSend
from web.utils.StockFile import StockFile
from web.utils import TemplateUtils
from web.db.dbexec import DBExec
from web.dataCenter import THSDataCenter
from web.busi import HandleLogService
from web.busi.StockAnalysis import *
from web.utils import Holiday
import logging
from web.db import Query
import re


class StockEventService(object):
    def __init__(self):
        self.thsData = THSDataCenter.THSData()
        self.thsDataOther = THSDataCenter.THSDataOther()
        self.db = DBExec(Query.QUERY_STOCK_EVENT, "")
        pass

    def update_all_stock_event(self):
        """
        更新所有stock事件
        :return:
        """
        stock_list = DBExec(Query.QUERY_STOCK, "FIND_STOCK_ALL").execute(None)
        # stock_list = [{'code': '300002'}]
        result = []
        logging.info("开始获取 stock事件 更新并发处理--->获取stock个数:%s" % (stock_list and len(stock_list) or 0))
        try:
            CommonUtils.start_many_thread(stock_list, handleSize=900, target=self.get_stock_event_batch,
                                          args=(result,), name="stock事件 更新并发处理", asyn=False)
        except Exception, e:
            logging.error("stock事件 更新并发处理--->失败:%s" % e)
        if len(result) > 0:
            logging.info("开始保存stock事件 --->处理个数：%s" % len(result))
            new_event_json = {}
            del_event_json = {}
            for res in result:
                self.save_stock_event(res, new_event_json, del_event_json)
            logging.info("开始保存stock事件 --->新增事件stock个数：%s" % len(new_event_json.keys()))
            logging.info("开始保存stock事件 --->删除事件stock个数：%s" % len(del_event_json.keys()))

            logging.info("开始保存stock事件 --->处理完成")
        else:
            logging.info("stock事件 更新并发处理--->未能获取stock事件")

    def save_stock_event(self, result, new_event_json, del_event_json):
        if result is None or len(result) == 0:
            return
        stock_code = result[0]['stock_code']
        event_list = self.db.setId("GET_STOCK_DAILY_STOCK_FUTURE").execute({'stock_code': stock_code}, print_sql=False)

        if bool(event_list):
            if isinstance(event_list, dict):
                event_list = [event_list]
            handle_date = event_list[len(event_list) - 1]['event_date']
            new_event, delete_event = self.__handle_event(event_list, result, handle_date)
            if bool(new_event):
                self.db.setId("INSERT_STOCK_EVENT").execute(new_event, print_sql=False)
                new_event_json[stock_code] = new_event
                self.important_event_handle(new_event)
            if bool(delete_event):
                self.db.setId("UPDATE_DAILY_STOCK_DEL").execute(delete_event, print_sql=False)
                del_event_json[stock_code] = delete_event
            self.db.commitTrans()
        pass

    def get_stock_event_batch(self, stock_list, result):
        """
        批量获取 时间
        :param stock_list:
        :param result:
        :return:
        """
        count = 0
        for stock in stock_list:
            res = self.thsDataOther.get_stock_important_event(stock['code'])
            if res:
                count += 1
                result.append(res)
        pass

    def __handle_event(self, old_event, new_event, handle_date):
        if handle_date is None:
            handle_date = 19700101
        old_json, old_arr = self.__create_json_arr(old_event, handle_date)
        new_json, new_arr = self.__create_json_arr(new_event, handle_date)

        if bool(old_json) is False:
            return new_arr, None
        if bool(new_json) is False:
            return None, None
        new_event = []
        delete_event = []
        for a in new_json:
            if a not in old_json:
                # 当原事件不含新日期的事件时
                new_event.extend(new_json[a]['__all'])
            else:
                c_new_json = new_json[a]
                c_old_json = old_json[a]
                # 过滤当天类型
                for b in c_new_json:
                    if b == '__all':
                        continue
                    if b not in c_old_json:
                        # 当原事件不包含当天的事件 新增
                        new_event.extend(c_new_json[b])
                    else:
                        # 判断是否删除 或者 更新
                        c_new_arr = c_new_json[b]
                        c_old_arr = c_old_json[b]
                        for oa in c_old_arr:
                            for na in c_new_arr:
                                if oa['content'] == na['content']:
                                    oa['flag'] = 1
                                    na['flag'] = 1
                        # 新增
                        t_new_arr = []
                        for ta in c_new_arr:
                            if ta['flag'] == 0:
                                t_new_arr.append(ta)
                        new_event.extend(t_new_arr)
                        t_old_arr = []
                        for ta in c_old_arr:
                            if ta['flag'] == 0:
                                t_old_arr.append(ta)
                        delete_event.extend(t_old_arr)
        for x in old_json:
            if x not in new_json:
                # 当新事件不含原日期的事件时
                delete_event.extend(old_json[x]['__all'])
            else:
                c_new_json = new_json[x]
                c_old_json = old_json[x]
                # 过滤当天类型
                for y in c_old_json:
                    if y not in c_new_json:
                        # 当原事件不包含当天的事件 新增
                        delete_event.extend(c_old_json[y])
        return new_event, delete_event

    @staticmethod
    def __create_json_arr(arr, handle_date):
        if arr is None or len(arr) == 0:
            return None, None
        res_json = {}
        res_arr = []
        for a in arr:
            trade_date = a['event_date']
            if int(trade_date) < int(handle_date):
                continue
            a['flag'] = 0
            res_arr.append(a)
            if trade_date in res_json:
                cur_json = res_json[trade_date]
                if a['type'] not in cur_json:
                    cur_json[a['type']] = []
                cur_json[a['type']].append(a)
                cur_json['__all'].append(a)
            else:
                res_json[trade_date] = {a['type']: [a], '__all': [a]}
        return res_json, res_arr

    def __extract_data(self, regex, content):
        p = re.compile(regex)
        m = p.search(content, re.S)
        if m:
            return m.groupdict()

    def important_event_handle(self, event_arr):
        cur_date = int(Holiday.get_cur_date())
        for event in event_arr:
            if event['type'] == 'tpts' or event['fpts']:
                regex = [r'停牌自(?P<tp>.*)起.*复牌日期(?P<fp>.{10,16})', r'”停牌(?P<tp>.*)，.*复牌日期(?P<fp>.{10,16})',
                         r'停牌自(?P<tp>.*)起.*']
                for r in regex:
                    result_json = self.__extract_data(r, str(event['content']))
                    if result_json:
                        if result_json['tp'] == '全天' or result_json['tp'] == '1天':
                            result_json['tp'] = str(event['content'])[0:10]
                        break
                if result_json is None:
                    logging.info("解析重要事件---》无法解析 tfp：%s" % str(event['content']))
                    HandleLogService.insert({'content': str(event['content']), 'type': 'important_event_handle'})
                    continue
                result_json['code'] = event['stock_code']
                if 'fp' not in result_json:
                    result_json['fp'] = None
                if result_json['fp']:
                    fp_date = result_json['fp'].split(" ")[0].replace("-", "")
                    # print fp_date
                    if int(fp_date) > cur_date:
                        DBExec(Query.QUERY_STOCK, "UPDATE_STOP_STOCK").execute(result_json)
                        pass
                else:
                    DBExec(Query.QUERY_STOCK, "UPDATE_STOP_STOCK").execute(result_json)
                    pass


if __name__ == '__main__':
    # s = StockEventService()
    # s.get_stock_event_batch([{'code': '002606'}], result)
    # s.save_stock_event(result[0])
    # s.update_all_stock_event()
    print len({'a':'','b':''}.keys())
    # HandleLogService.insert({'content': '11', 'type': 'important_event_handle'})
    # s = StockEventService()
    # event_list = s.db.setId("GET_STOCK_TP_EVENT").execute(None)
    # StockEventService().important_event_handle(event_list)
    # content_arr = ['2017-10-20因“盘中临时停牌”停牌09:30:00-10:00:00，复牌日期2017-10-20 10:00',
    #                '2017-01-12因“临时停牌”停牌自2017-01-12起连续停牌，复牌日期2017-01-13 09:30[查看公告]',
    #                '2017-11-01因“临时停牌”停牌自2017-11-01起连续停牌[查看公告]', ]
    # regex = r'停牌自(?P<tp>.*)起.*'
    # p = re.compile(regex)
    # for c in content_arr:
    #     m = p.search(c, re.S)
    #     print c
    #     if m:
    #         print m.groupdict()
