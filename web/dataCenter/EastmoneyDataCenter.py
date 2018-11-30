# coding:utf-8

import json
import logging
import time

from web.utils import StringUtils, Holiday
from web.utils.webclient import WebClient
from bs4 import BeautifulSoup
from web.busi.SysDictService import DictService


# 个股解禁历史 http://data.eastmoney.com/dxf/q/601997.html
# http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?token=70f12f2f4f091e459a279469fe49eca5&st=ltsj&
# sr=1&p=1&ps=50&type=XSJJ_NJ_PC&js=var%20raxPSCWc={pages:(tp),data:(x)}&filter=(gpdm=%27601997%27)&rt=51138864
# 所有解禁 http://data.eastmoney.com/dxf/detail.aspx?market=all
# 按日期解禁 http://data.eastmoney.com/dxf/detail.aspx?market=all&startdate=2018-07-31&enddate=2018-07-31
# 股票回购 http://data.eastmoney.com/gphg/
# 分红 http://data.eastmoney.com/yjfp/
# 股票增减持 http://data.eastmoney.com/executive/gdzjc.html


class EastmoneyData(object):
    """
    东方财富
    """

    @staticmethod
    def getCurData(code):
        """

        :param code:
        :return:
        """
        client = WebClient()
        url = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id=%s%s&token=4f1862fc3b5e77c150a2b985b12db0fd&cb=jQuery183&_=%s'
        resp = client.get(url % (code, StringUtils.stock_code_type_int(code), int(time.time())))
        if resp.status == 200:
            da = resp.data.split("(", 2)[1]
            data = json.loads(da[0:len(da) - 1])
            d = data['Value']
            if bool(d) is False:
                logging.error("eastmoney 获取数据错误：%s" % code)
                return None
            res = {
                'high_end': float(d[23]),  # 涨停
                'low_end': float(d[24]),  # 跌停
                'high_price': float(d[30]),  # 最高
                'low_price': float(d[32]),  # 最低
                'price': float(d[25]),  # 当前价
                'open_price': float(d[28]),  # 开盘价
                'average_price': float(d[26]),  # 均价
                'turnover_rate': float(d[37]),  # 换手
                'close_price': float(d[34]),  # 昨收
                'growth': float(d[29]),  # 涨幅
                'amplitude': float(d[50]),  # 振动幅度
                'volume_transaction': float(d[31]),  # 成交量
                'turnover': float(d[35].replace('万', '').replace('亿', '')),  # 成交额
                'stock_code': d[1],
                'chg': d[27],
                'rs': 'eastmoney'

            }
            return res
        else:
            logging.error("【eastmoney】获取[%s]实时数据出现请求错误,请求码:%s" % (code, resp.status))
        return None

    def get_fund_company(self):
        """
        获取基金公司数据
        :return:
        """
        url = "http://fund.eastmoney.com/company/default.html"
        c = WebClient()

        resp = c.get(url)
        result = []
        if resp.status == 200:
            trs = BeautifulSoup(resp.data, "html.parser").find(id='gspmTbl').select("tr")
            for i in range(1, len(trs)):
                tr = trs[i]
                tds = tr.select('td')
                name = str(tds[1].string)
                found_date = str(tds[3].string)
                code = tds[1].select('a')[0].attrs['href'].split("/")[2].split(".")[0]
                level = 0
                capacity = 0
                sprite_star1 = tds[4].find_all(class_='sprite-star1')
                if bool(sprite_star1):
                    level = len(sprite_star1)
                sprite_star5 = tds[4].find_all(class_='sprite-star5')
                if bool(sprite_star5) and level == 0:
                    level = len(sprite_star5)
                # capacity_str = tds[5].text.split(" ")[0].replace(",", "").replace("-", "").strip()
                capacity_str = tds[5].attrs['data-sortvalue']
                capacity = bool(capacity_str) and float(capacity_str) or 0
                obj = {"name": name, "company_level": level, "found_date": found_date, "capacity": capacity,
                       "code": code}
                result.append(obj)


        else:
            logging.error("【eastmoney】获取基金公司数据异常请求错误,请求码:%s" % (resp.status))
        return result

    def get_fund_list_by_company(self, code):
        """
        根据公司code获取公司下面所有的基金
        :param code:
        :return:
        """
        url = "http://fund.eastmoney.com/Company/%s.html" % code
        c = WebClient()

        resp = c.get(url)
        result = []
        if resp.status == 200:
            trs = []
            kfs = BeautifulSoup(resp.data, "html.parser").find(id='kfsFundNetWrap')
            if kfs:
                trs = kfs.select("tr")
            hb_trs = []
            hb = BeautifulSoup(resp.data, "html.parser").find(id='HBLCFundNetCon')
            if hb:
                hb_trs = hb.select("tr")
            cnf = BeautifulSoup(resp.data, "html.parser").find(id='CNFundNetCon')
            cn_trs = []
            if cnf:
                cn_trs = cnf.select("tr")
            if len(hb_trs) > 0:
                if len(trs) > 0:
                    trs.extend(hb_trs[1:])
                else:
                    trs = hb_trs
            if len(cn_trs) > 0:
                if len(trs) > 0:
                    trs.extend(cn_trs[1:])
                else:
                    trs = cn_trs
            for i in range(1, len(trs)):
                tr = trs[i]
                tds = tr.select('td')
                if str(tds[0].string) == '暂无数据':
                    logging.error("【eastmoney】获取基金公司[%s]无数据" % code)
                    break
                name_code = tds[0].select("a")
                name = str(name_code[0].attrs['title'])
                code = str(name_code[1].string)
                fund_type = str(tds[2].string)
                result.append({"name": name, "code": code, "type": fund_type})

        else:
            logging.error("【eastmoney】获取基金公司[%s]数据异常,请求码:%s" % (code, resp.status))
        return result

    def get_fund_stock(self, code, month, year=""):
        """
        获取基金股票数据
        :param month:
        :param year:
        :return:
        """
        url = "http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code=%s&topline=10" \
              "&year=%s&month=%s&rt=%s" % (code, year, month, int(time.time()))
        c = WebClient()
        resp = c.get(url)
        result = []
        if resp.status == 200:
            # print resp.data
            h = resp.data.split("content:\"")[1].split("arryear:\"")[0]
            if bool(h) is False:
                logging.error("【eastmoney】获取基金[%s]stock 数据：无数据" % (code))
                return result
            html = BeautifulSoup(h, "html.parser")
            trs = html.select("table")[0].select('tr')
            end_date = str(html.find_all(class_='right')[0].select('font')[0].string)
            if end_date != DictService().get_fund_end_date():
                return result
            for i in range(1, len(trs)):
                tr = trs[i]
                tds = tr.select('td')
                stock_code = str(tds[1].string)
                stock_name = str(tds[2].string)
                scale = float(str(tds[6].string.replace("%", "")))
                quantity = float(str(tds[7].string.replace(",", "")))
                mc = float(str(tds[8].string.replace(",", "")))
                result.append({"stock_code": stock_code, "stock_name": stock_name, "mc": mc, "scale": scale,
                               "quantity": quantity, "end_date": end_date, "fund_code": code})

        else:
            logging.error("【eastmoney】获取基金公司[%s]数据异常,请求码:%s" % (code, resp.status))
        return result

    def get_fund_daily(self, code):
        url = "https://fundmobapi.eastmoney.com/FundMApi/FundBaseTypeInformation.ashx?callback=jQuery%s&" \
              "FCODE=%s&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0&Uid=&_=%s" % (
                  int(time.time()), code, int(time.time()))
        c = WebClient()
        resp = c.get(url)
        res = {}
        if resp.status == 200:
            # print resp.data
            resp.data = resp.data.encode("utf-8")
            h = resp.data.split("(", 1)[1]
            h = h[0:len(h) - 1]
            if bool(h) is False:
                logging.error("【eastmoney】获取基金[%s] daily 数据：无数据" % (code))
                return None
            obj_json = json.loads(h)['Datas']
            res = {}
            res["fund_code"] = code
            res["fund_name"] = obj_json['SHORTNAME']
            res['cur_price'] = obj_json['DWJZ']
            res['growth'] = float(obj_json['RZDF'])
            res['sell'] = obj_json['SHZT']
            res['buy'] = obj_json['SGZT']
        else:
            logging.error("【eastmoney】获取基金公司[%s]数据异常,请求码:%s" % (code, resp.status))
        return res

    def get_stock_tfp(self, sType='tp', pageSize=50):
        """
        停复牌 2 停牌 6 复牌
        :return:

        var LISSPdZE = {
            pages: 4,
            data: ["300187,永清环保,2018-04-09 09:30,2018-10-09 15:00,连续停牌,拟筹划重大资产重组,创业板,2018-04-09,2018-10-10"]
        }
        """
        tf = '2'
        if sType == 'fp':
            tf = '6'
        url = 'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=FD&sty=SRB&st=%s' \
              '&sr=-1&p=1&ps=%s&js=var%%20mzsIinmN={pages:(pc),data:[(x)]}&mkt=1&fd=%s&rt=51054649' \
              % (tf, pageSize, Holiday.get_cur_date(splitType="-"))
        c = WebClient()
        resp = c.get(url)
        result = []
        if resp.status == 200:
            # print resp.data
            resp.data = resp.data.encode("utf-8")

            h = resp.data.split("data:", 1)[1].replace("}", "")
            data = json.loads(h)
            if len(data) <= 0:
                logging.error("【eastmoney】获取停复牌数据：无数据")
                return None
            result = []
            for i in range(0, len(data)):
                arr = data[i].split(",")
                res = {'stock_code': arr[0], 'stock_name': arr[1], 'tp': arr[2], 'fp': None}
                if len(arr) == 9:
                    res['fp'] = arr[8]
                result.append(res)

        else:
            logging.error("【eastmoney】获取停复牌数据异常,请求码:%s" % (resp.status))
        return result

    def get_stock_history_jj_data(self, code):
        """
        获取历史解禁数据
        :param code:
        :return:
        {
        "gpdm": "601997",
        "ltsj": "2019-08-16T00:00:00",
        "gpcjjgds": 10.0,
        "jjsl": 93385.3442,
        "jjsz": 1113153.302864,
        "xsglx": "首发原股东限售股份",
        "jjqesrzdf": "-",
        "jjhesrzdf": "-",
        "yltsl": 217281.8537,
        "wltsl": 12577.3363,
        "zb": 0.753736683760247,
        "mkt": "sh",
        "sname": "贵阳银行",
        "newPrice": 11.92,
        "zzb": 0.406271962413163,
        "kjjsl": 93385.3442,
        "kjjsz": 1113153.302864
        }
        """
        url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?token=70f12f2f4f091e459a279469fe49eca5' \
              '&st=ltsj''&sr=-1&p=1&ps=50&type=XSJJ_NJ_PC&js=var%%20FPkxTgHV={pages:(tp),data:(x)}&filter' \
              '=(gpdm=%%27%s%%27)&rt=51055517' \
              % code
        c = WebClient()
        resp = c.get(url)
        if resp.status == 200:
            resp.data = resp.data.encode("utf-8")
            h = resp.data.split("data:", 1)[1]
            h = h[0:len(h) - 1]
            return self.__handl_jj_data(h)
        else:
            logging.error("【eastmoney】获取解禁历史数据,请求码:%s code:" % (resp.status, code))
            return None

    def get_jj_data_by_date(self, start_date=None, end_date=None):
        """
        获取历史解禁数据
        :param start_date:
        :param end_date:
        :return:
        """
        if bool(start_date) is False:
            start_date = Holiday.get_cur_date(splitType="-")
        if bool(end_date) is False:
            end_date = Holiday.get_cur_date(splitType="-")
        url = 'http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get?type=XSJJ_NJ_PC&' \
              'token=70f12f2f4f091e459a279469fe49eca5&st=kjjsl&sr=-1&p=1&ps=10&filter=(mkt=)(ltsj%%3E' \
              '=^%s^%%20and%%20ltsj%%3C=^%s^)&js=var%%20HtwQmsuo=(x)' \
              % (start_date, end_date)
        c = WebClient()
        resp = c.get(url)

        if resp.status == 200:
            resp.data = resp.data.encode("utf-8")
            h = resp.data.split("=", 1)[1]
            return self.__handl_jj_data(h)
        else:
            logging.error("【eastmoney】获取解禁历史数据,请求码:%s [%s:%s]" % (resp.status, start_date, end_date))
            return None

    def __handl_jj_data(self, data_str):
        """
        处理解禁数据
        :param data_str:
        :return:
        {
        "gpdm": "601997",
        "ltsj": "2019-08-16T00:00:00",
        "gpcjjgds": 10.0,
        "jjsl": 93385.3442,
        "jjsz": 1113153.302864,
        "xsglx": "首发原股东限售股份",
        "jjqesrzdf": "-",
        "jjhesrzdf": "-",
        "yltsl": 217281.8537,
        "wltsl": 12577.3363,
        "zb": 0.753736683760247,
        "mkt": "sh",
        "sname": "贵阳银行",
        "newPrice": 11.92,
        "zzb": 0.406271962413163,
        "kjjsl": 93385.3442,
        "kjjsz": 1113153.302864
        }
        """
        # print resp.data
        result = []
        data = json.loads(data_str)
        if len(data) <= 0:
            logging.error("【eastmoney】获取解禁历史数据：无数据")
            return result
        for i in range(0, len(data)):
            d = data[i]
            res = {'stock_code': d['gpdm'], 'stock_name': d['sname'], 'jj_date': d['ltsj'].split('T')[0],
                   'jjsl': d['jjsl'], 'jjsz': d['jjsz'], 'jjlx': d['xsglx'], 'jjgds': d['gpcjjgds'],
                   'wjjsl': d['wltsl'], 'scale': d['zzb'], 'source_type': 'eastmoney'}
            result.append(res)
        return result

    def get_stock_money(self, code):
        """
        资金流入
        :return:
        """
        url = 'http://ff.eastmoney.com//EM_CapitalFlowInterface/api/js?type=hff&rtntype=2' \
              '&js=({data:[(x)]})&cb=var%%20aff_data' \
              '=&check=TMLBMSPROCR&acces_token=1942f5da9b46b069953c873404aad4b5&id=%s%s&_=1535640771482' % \
              (code, StringUtils.stock_code_type_int(code))
        c = WebClient()
        resp = c.get(url)
        result = []
        if resp.status == 200:
            resp.data = resp.data.encode("utf-8")
            h = resp.data.split("data:", 1)[1]
            trs = json.loads(h[0:len(h) - 2])[0]
            for i in range(0, len(trs)):
                tds = trs[i].split(',')
                trade_date = tds[0]
                close_price = tds[11]
                growth = tds[12].replace("%", '')
                m_amt = tds[1].replace("万", '')
                m_ratio = tds[2].replace("%", '')
                sb_amt = tds[3].replace("万", '')
                sb_ratio = tds[4].replace("%", '')
                b_amt = tds[5].replace("万", '')
                b_ratio = tds[6].replace("%", '')
                md_amt = tds[7].replace("万", '')
                md_ratio = tds[8].replace("%", '')
                s_amt = tds[9].replace("万", '')
                s_ratio = tds[10].replace("%", '')
                j = {'trade_date': trade_date, 'stock_code': code, 'close_price': close_price,
                     'growth': growth, 'm_amt': m_amt, 'm_ratio': m_ratio, 'sb_amt': sb_amt, 'sb_ratio': sb_ratio,
                     'b_amt': b_amt, 'b_ratio': b_ratio, 'md_amt': md_amt, 'md_ratio': md_ratio, 's_amt': s_amt,
                     's_ratio': s_ratio
                     }
                result.append(j)
        return result

    # url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=0027452&sty=CTBF&st=z&sr=&p=&ps=&cb=var%20pie_data=&js=(x)&token=28758b27a75f62dc3065b81f7facb365&_=1535642715895'
    # var pie_data = "2,002745,木林森,17.85,1.48%,11041.91,791, 27169530,-4965148,2220.44,3.82%, 187317507,-99102819,8821.47,15.17%, 204126281,-321152896,-11702.66,-20.12%, 163060491,-156452944,660.75,1.14%"

    def get_zjc_stock(self, code, page=1):
        """
        var srVevXgQ={pages:1,data:["601008,连云港,3.15,-0.63,连云港港口集团有限公司,增持,12.98,0.01,二级市场,49187.2518,48.45,49187.2518,48.45,2018-11-01,2018-11-01,2018-11-02,0.0128"
        :param code:
        :param page:
        :return:
        """
        url = "http://data.eastmoney.com/DataCenter_V3/gdzjc.ashx?pagesize=50&page=%s&js=var%%20srVevXgQ&param=&sortRule=-1&sortType=BDJZ&tabid=all&code=%s&name=&rt=51380939" % (
        page, code)
        c = WebClient()
        resp = c.get(url)
        result = []
        if resp.status == 200:
            resp.data = resp.data.decode("gbk")
            h = resp.data.split("data:", 1)[1].split(",\"url")[0]
            data = json.loads(h)
            for i in range(0, len(data)):
                arr = data[i].split(',')
                code = arr[0]
                name = arr[1]
                gd_name = arr[4]
                trade_type = arr[5]
                trade_quantity = arr[6]
                trade_lt_ratio = arr[7].replace("-", "")
                sc = arr[8]
                z_quantity = arr[9].replace("-", "")
                zg_ratio = arr[10].replace("-", "")
                lt_quantity = arr[11].replace("-", "")
                lt_ratio = arr[12].replace("-", "")
                trade_start = arr[13].replace("-", "")
                trade_end = arr[14].replace("-", "")
                notice_date = arr[15].replace("-", "")
                trade_zg_ratio = arr[16].replace("-", "")
                j = {"stock_code": code, "name": name, "gd_name": gd_name, "trade_type": trade_type,
                     "trade_quantity": trade_quantity, "trade_lt_ratio": trade_lt_ratio,
                     "trade_zg_ratio": trade_zg_ratio,
                     "sc": sc, "z_quantity": z_quantity, "zg_ratio": zg_ratio, "lt_quantity": lt_quantity,
                     "lt_ratio": lt_ratio, "notice_date": notice_date, "trade_start": trade_start,
                     "trade_end": trade_end}
                result.append(j)
        return result


if __name__ == '__main__':
    em = EastmoneyData()
    # print em.get_jj_data_by_date(end_date='2018-07-18')
    print em.get_zjc_stock('601997')
