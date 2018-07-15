# coding:utf-8

import json
import logging
import time

from web.utils import StringUtils, Holiday
from web.utils.webclient import WebClient
from bs4 import BeautifulSoup

client = WebClient()


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
            trs = BeautifulSoup(resp.data, "html.parser").find(id='kfsFundNetWrap').select("tr")
            hb_trs = BeautifulSoup(resp.data, "html.parser").find(id='HBLCFundNetCon').select("tr")
            cn_trs = BeautifulSoup(resp.data, "html.parser").find(id='CNFundNetCon').select("tr")
            if len(hb_trs) > 0:
                if len(trs) > 0:
                    result.extend(hb_trs[1:])
                else:
                    trs = hb_trs
            if len(cn_trs) > 0:
                if len(trs) > 0:
                    result.extend(cn_trs[1:])
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


if __name__ == '__main__':
    em = EastmoneyData()
    print em.get_stock_tfp()
