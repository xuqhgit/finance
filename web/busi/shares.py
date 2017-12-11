# coding=utf-8
import random

from flask import url_for

from web.utils.webclient import WebClient
from web.utils.StringUtils import StringUtils
from web.utils import FileUtils
from bs4 import BeautifulSoup
import json
import os
import xdrlib, sys
import xlrd
import time
import thread
import logging
import numpy

_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# shares文件夹
_shares_dir = os.path.join(_dir, 'static/file/shares')
if not os.path.isdir(_shares_dir):
    os.makedirs(_shares_dir)
# shares日数据
_cur_01_shares_dir = os.path.join(_shares_dir, '01')
if not os.path.isdir(_cur_01_shares_dir):
    os.makedirs(_cur_01_shares_dir)
# 腾讯当日shares excel data
shareCodeXlsUrl = 'http://stock.gtimg.cn/data/get_hs_xls.php?id=[code]&type=1&metric=chr'

minData = 'http://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_[code]&code=[code]&r=[random]'
# 腾讯当前shares 数据
TX_CUR_DATA_URL = 'http://web.sqt.gtimg.cn/q=%s?r=%s'
# THS 日数据
THS_DAY_DATA_URL = 'http://d.10jqka.com.cn/v2/line/hs_%s/01/%s.js?_t=%s'

STOCK_DIR = _shares_dir


class Shares(object):
    """shares info"""
    # 获取shares data url
    sharesDataUrlPrefix = 'http://d.10jqka.com.cn/v2/time/sh_600087/last.js'
    shareDict = {
        "ranka": "沪深(A)",
        "rankb": "沪深(B)",
        "rankash": "沪市(A)",
        "rankbsh": "沪市(B)",
        "rankasz": "深市(A)",
        "rankbsz": "深市(B)",
        "rankchuangye": "创业板",
        "rankzhongxiao": "中小板",
        "rankbond": "债券",
        "rankindex": "基金"
    }

    # 获取shares code url
    # shareCodeUrl = 'http://bbs.10jqka.com.cn/codelist.html'


    def __init__(self):
        self.client = WebClient()
        pass

    def getCurSharesData(self):
        # self.client.get(self.shareCodeUrl)
        # self.client.get(self)
        pass

    def downloadExcelFile(self):
        _cur_shares_dir = os.path.join(_shares_dir, time.strftime('%Y%m%d', time.localtime(time.time())) + '/excel')
        if not os.path.isdir(_cur_shares_dir):
            os.makedirs(_cur_shares_dir)
        for (k, v) in self.shareDict.items():
            url = 'http://stock.gtimg.cn/data/get_hs_xls.php?id=%s&type=1&metric=chr' % k
            print '下载:%s excel文件.....' % v
            xls = self.client.get(url)
            f = file(_cur_shares_dir + '/%s.xls' % v, "wb")
            f.write(xls.data)
            f.close()
        pass

    def getCurShares(self):
        pass

    def getExcelData(self, date, fileName):
        fileUrl = '%s/%s/excel/%s.xls' % (_shares_dir, date, fileName)
        list = []
        try:
            print '读取:%s/excel/%s.xls 文件中....' % (date, fileName)
            data = xlrd.open_workbook(u'%s' % fileUrl)
            table = data.sheet_by_name('sheet 1')
            nrows = table.nrows  # 行数
            colnames = table.row_values(1)  # 某一行数据
            for rownum in range(1, nrows):
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

    def getMinDataByCode(self, code):
        url = 'http://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_%s&code=%s&r=%s' % (
            code, code, random.random())
        js = self.client.get(url)
        da = len(js.data.split('=', 2)) > 1 and js.data.split('=', 2)[1] or {}
        return da

    def getMinData(self, date, name, rank):
        list = self.getExcelData(date, name)
        listLen = len(list)
        _cur_shares_dir = os.path.join(_shares_dir,
                                       time.strftime('%Y%m%d', time.localtime(time.time())) + '/json/' + rank)
        if not os.path.isdir(_cur_shares_dir):
            os.makedirs(_cur_shares_dir)
        minLen = 50
        a = listLen / minLen
        b = listLen % minLen
        for i in range(0, a + 1):
            thread.start_new_thread(self.__getSharesThread,
                                    (list, i * minLen + (i == 0 and 1 or 0), i * minLen + (i == a and b or minLen),
                                     _cur_shares_dir))
        if rank == 'sha':
            self.__saveJSon('sh000001', _cur_shares_dir)
        elif rank == 'sza':
            self.__saveJSon('sz399001', _cur_shares_dir)
        elif rank == 'cy':
            self.__saveJSon('sz399006', _cur_shares_dir)
        return

    def getDmi(self, type):

        pass

    def __getSharesThread(self, list, fromIndex, toIndex, cur_shares_dir):
        if toIndex == 0:
            return
        for num in range(fromIndex, toIndex):
            data = list[num]
            sharesCode = data[0]
            self.__saveJSon(sharesCode, cur_shares_dir)
            self.__saveJSonThs(sharesCode, cur_shares_dir)
            self.__saveJSonThsm(sharesCode, cur_shares_dir)

    def __saveJSon(self, sharesCode, dir):
        print '下载:%s 时分数据\n' % (sharesCode)
        url = 'http://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_%s&code=%s&r=%s' % (
            sharesCode, sharesCode, random.random())
        js = self.client.get(url)
        da = len(js.data.split('=', 2)) > 1 and js.data.split('=', 2)[1] or None
        if da:
            f = file(dir + '/%s.json' % sharesCode, "wb")
            f.write(da)
            f.close()
        else:
            print '忽略' + sharesCode
        pass

    def __saveJSonThs(self, sharesCode, dir):
        print '下载:%s 时分数据(同)\n' % (sharesCode)
        sharesCode = sharesCode[2:8]
        url = 'http://d.10jqka.com.cn/v2/time/hs_%s/last.js?_t=%s' % (
            sharesCode, random.random())
        js = self.client.get(url)
        da = len(js.data.split('(', 2)) > 1 and js.data.split('(', 2)[1] or None
        if da:
            da = da[0:len(da) - 1]
            f = file(dir + '/%s.json' % sharesCode, "wb")
            f.write(da)
            f.close()
        else:
            print '忽略' + sharesCode
        pass

    def __saveJSonThsm(self, sharesCode, dir):
        print '下载:%s 时分数据(m)\n' % (sharesCode)
        sharesCode = sharesCode[2:8]
        url = 'http://d.10jqka.com.cn/v2/moneyflow/hs_%s/last.js?_t=%s' % (
            sharesCode, random.random())
        js = self.client.get(url)
        da = len(js.data.split('(', 2)) > 1 and js.data.split('(', 2)[1] or None
        if da:
            da = da[0:len(da) - 1]
            f = file(dir + '/%s_m.json' % sharesCode, "wb")
            f.write(da)
            f.close()
        else:
            print '忽略' + sharesCode
        pass


class SharesAnalyse(object):
    """

    """

    @staticmethod
    def getrsi(data, avg=6, r=2):
        dlen = len(data)
        arr = []
        for i in range(1, dlen):
            s = data[i][4]
            pres = data[i - 1][4]
            r = s - pres
            print "%s=%s - %s" % (r, s, pres)
            arr.append(r)
        rarr = []

        for i in range(0, dlen):
            d = i - avg
            d = d >= 0 and d or 0
            l = arr[d:i]
            lista = [a for a in l if a >= 0]
            listb = [a for a in l if a < 0]
            alen = len(lista) == 0 and 1 or len(lista)
            blen = len(listb) == 0 and 1 or len(listb)
            suma = round(sum(lista), 3)
            sumb = round(abs(sum(listb)), 3)
            if suma + sumb > 0:
                print suma / (suma + sumb)
                rarr.append(round(suma / (suma + sumb) * 100, 3))
        return rarr

    @staticmethod
    def avgdif(data, avga=5, avgb=10):
        if avga >= avgb:
            return None
        a = SharesAnalyse.getAvgData(data, avg=[avga, avgb])
        return numpy.array(a)[:, 0] - numpy.array(a)[:, 1]

    @staticmethod
    def getAvgData(data, avg=[5], r=2):
        """
        获取平均值
        :param data: list类型数据
        :param avg: 平均数分母大小 list
        :return: 平均数list
        """
        dlen = len(data)
        arg = []
        alen = len(avg)
        for i in range(1, dlen + 1):
            arr = []
            for j in range(0, alen):
                if i < avg[j]:
                    arr.append(round(sum(data[0:i]) / float(i), r))
                else:
                    arr.append(round(sum(data[i - avg[j]:i]) / float(avg[j]), r))
            arg.append(arr)
        return arg

    @staticmethod
    def getDayData(code=None, year='last', client=None):
        """
        data数据格式20160415,16.90,17.13,16.75,17.01,12749919,216191310.00,1.369,
        时间,开,高,低,收,成交量,成交额,换手
        "rt": "0930-1130,1300-1500",
        "total": "1389",
        "year": {
            "2010": 116,
            "2011": 240,
            "2012": 242,
            "2013": 238,
            "2014": 245,
            "2015": 239,
            "2016": 69
        },
        "start": "20100713",
        "num": 140,
        "name": "\u5de8\u661f\u79d1\u6280",
        获取同花顺日线数据
        :param code: 股票代码 格式sh+代码
        :param year: 年份 默认近期
        :param client: 客户端
        :return: 返回同花顺dict格式数据
        """
        file_url = '%s/%s.json' % (_cur_01_shares_dir, code)
        file = FileUtils.get_file(file_url)
        if file is None:
            file = SharesAnalyse.downloadSharesDayData(code, year=year, client=client)
        if file:
            return json.loads(file)
        return None




    @staticmethod
    def getCurShareData(code=None, client=None):
        """
        获取实时的股票头部数据
        :param code: 股票代码 格式为:sh+代码
        :param client: 浏览器客户端
        :return: 获取指定格式的dict数据
        """
        if client is None:
            client = WebClient()
        url = TX_CUR_DATA_URL % (code, random.random())
        req = client.get(url)
        if req.status == 200:
            splitStr = '="'
            da = len(req.data.split(splitStr, 2)) > 1 and req.data.split(splitStr, 2)[1] or None
            if da is None:
                return None
            da = da[0:len(da) - 1].replace("~~~", "~~")
            strs = da.split('~~', 2)
            b = strs[0].split('~', 7)
            if float(b[3]) == 0 or float(b[5]) == 0:
                return None
            c = b[7].split('~', 34)

            a = strs[1].split('~', 9)
            try:

                result = {'zt': float(a[6]),  # 涨停
                          'dt': float(a[7]),  # 跌停
                          'hp': float(a[0]),  # 最高
                          'lp': float(a[1]),  # 最低
                          'cur': float(b[3]),  # 当前价
                          'op': float(b[4]),  # 开盘价
                          'hs': float(c[31]),  # 换手
                          'zs': float(b[4]),  # 昨收
                          'zf': float(c[25]),  # 涨幅
                          'zdf': float(a[2]),  # 振动幅度
                          'zd': float(c[24])  # 涨跌
                          }
            except Exception, e:
                print code, e, req.data
                return None

            return result
        else:
            logging.error("获取[%s]实时数据出现请求错误,请求码:%s" % (code, req.status))
            return None

    @staticmethod
    def Ktype(cur=0, openp=0, hp=0, lp=0):
        """
        返回k线类型
        :param cur: 当前价格 或者收盘价格
        :param openp: 开盘价格
        :param hp: 最高价格
        :param lp: 最低价格
        :return: 返回k线类型
        """
        # 上影响差值
        upDif = cur > openp and hp - cur or hp - openp
        # 下影线差值
        downDif = cur > openp and openp - lp or cur - lp
        # 中部差值
        midDif = cur - openp
        # 最大差值
        maxDif = hp - lp
        # 开盘于当前价一致 则有 跌停,涨停,T字型,倒T,十字星
        if midDif == 0:
            if upDif == 0 and downDif == 0:
                return 'Z'
            elif upDif == 0:
                return 'T'
            elif downDif == 0:
                return 'L'
            else:
                return 'Y'
        # 无上影线下影线
        if upDif == 0 and downDif == 0:
            return 'C'
        # 无上影线
        if upDif == 0:
            if downDif / abs(midDif) >= 2:
                return 'q'
            else:
                return 'p'
        # 无下影线
        if downDif == 0:
            if upDif / abs(midDif) >= 2:
                return 'd'
            else:
                return 'b'
        # 类似十字星
        if abs(midDif) / maxDif <= 0.3:
            return 'Y'
        return 'H'

    @staticmethod
    def dkpre(cur=0, openp=0, hp=0, lp=0):

        """
        多空比例
        :param cur: 当前价格或者收盘价格
        :param openp: 开盘价格
        :param hp: 最高价格
        :param lp: 最低价格
        :return: 返回多空比
        """
        dif = hp - lp
        k = hp - cur
        d = cur - lp
        return round(d / dif, 2)

    @staticmethod
    def getAllSharesDayData(func):
        title = "沪深(A)"
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        list = Shares().getExcelData(date, title)
        result = []
        if list is None:
            Shares().downloadExcelFile()
            list = Shares().getExcelData(date, "沪深(A)")

        if list:
            for i in range(1, len(list) - 1):
                code = list[i][0][2:8]
                data = SharesAnalyse.getDayData(code=code)
                if data is None:
                    continue
                r = func(data)
                if r:
                    result.append({"code": code, "data": r})
        else:
            print "获取[%s]excel数据异常" % title
        return result

    @staticmethod
    def getJYX(data, maxnext=3):
        """
        获取假阴线数据
        :param data:
        :return:
        """
        if maxnext < 0:
            return None
        arr = StringUtils.str_2_arr(data['data'].split(";"))
        dlen = len(arr)
        res = []

        for i in range(0, dlen):
            pre = arr[i > 0 and i - 1 or 0]
            cur = arr[i]
            # 时间,开,高,低,收,成交量,成交额,换手
            if pre[7] and pre[7] > 0:
                hpre = cur[7] / pre[7]
                if cur[1] > cur[4] and cur[4] >= pre[4] and cur[2] == cur[1]:
                    r = []
                    r.append(cur)
                    for j in range(1, maxnext + 1):
                        r.append(i + j < dlen and arr[i + j] or None)
                    res.append(r)
        return res

    @staticmethod
    def downloadSharesDayData(code, year=None, client=None):
        logging.info("下载[%s] 日数据" % code)
        if client is None:
            client = WebClient()
        url = THS_DAY_DATA_URL % (code, year, random.random())
        req = client.get(url)
        if req.status == 200:
            pre_data = req.data.split('(', 2)[1]
            data = pre_data[0:len(pre_data) - 1].decode('unicode_escape')
            f = file(_cur_01_shares_dir + '/%s.json' % code, "wb")
            f.write(data)
            f.close()
            return data
        else:
            logging.error("下载[%s]日数据出错->status:%s" % (code, req.status))
        return None

    @staticmethod
    def getKDJ(data, tc=9):
        """
        获取数据的KDJ值
        :param data:
        :return:
        """
        dlen = len(data)
        arr = numpy.array(data)
        k = 50
        d = 50
        for i in range(0, dlen):
            a = arr[tc <= i + 1 and i + 1 - tc or 0:i + 1]
            h = a[:, 2].max()
            l = a[:, 3].min()
            c = arr[i, 4]
            rsv = (c - l) / (h - l) * 100
            k = rsv / 3 + 2 * k / 3
            d = k / 3 + 2 * d / 3
            j = 3 * k - 2 * d
            print arr[i, 0], round(k, 2), round(d, 2), round(j, 2)

    @staticmethod
    def getBias(data, tc=[6]):
        dlen = len(data)
        arr = []
        tlen = len(tc)
        for i in range(1, dlen + 1):
            r = []
            for j in range(0, tlen):
                if i < tc[j]:
                    avg = round(sum(data[0:i]) / float(i), 2)
                else:
                    avg = round(sum(data[i - tc[j]:i]) / float(tc[j]), 2)
                bias = (data[i - 1] - avg) / avg
                r.append(bias * 100)
            arr.append(r)
        return arr

    @staticmethod
    def getBoll(data, d=20):
        dlen = len(data)
        mdata = numpy.array(data)
        arr = []
        for i in range(1, dlen + 1):
            r = []
            if i < d:
                nd = data[0:i]
                m = i
                avg = round(sum(nd) / float(m), 2)
            else:
                nd = data[i - d:i]
                m = d
                avg = round(sum(nd) / float(m), 2)
            # if m>1:
            #     _nd = nd[0:m - 1]
            # else:
            #     _nd = nd
            # mb = round(sum(_nd) / float(m > 1 and m - 1 or m), 2)
            md = (sum((nd - avg) ** 2) / m) ** 0.5
            mb = avg
            up = mb + 2 * md
            dn = mb - 2 * md
            r.extend([avg, md, up, dn])
            print r
        arr.append(r)
        return arr

    @staticmethod
    def getMacd(data, avga=12, avgb=26, avgc=9):

        dlen = len(data)
        a = 0
        b = 0
        aArr = []
        bArr = []
        for i in range(0, dlen):
            a = a * (avga - 1) / (avga + 1) + 2 * data[i] / (avga + 1)
            b = b * (avgb - 1) / (avgb + 1) + 2 * data[i] / (avgb + 1)
            aArr.append(a)
            bArr.append(b)
        dif = numpy.array(aArr) - numpy.array(bArr)

        print dif


def getJYXRes():
    arr = SharesAnalyse.getAllSharesDayData(SharesAnalyse.getJYX)
    alen = len(arr)
    sum = 0
    one = 0
    two = 0
    three = 0
    for i in range(0, alen):
        ar = arr[i]['data']
        arlen = len(ar)
        for j in range(0, arlen):
            a = ar[j]
            sum += 1
            r = []
            l = len(a)
            for k in range(1, l):
                if a[k]:
                    p = round((a[k][4] - a[k - 1][4]) / a[k - 1][4], 2)
                    if k == 1 and p > 0:
                        one += 1
                    if k == 2 and p > 0:
                        two += 1
                    if k == 3 and p > 0:
                        three += 1
                    r.append(p)
    print "sum:%s,one:%s,tow:%s,three:%s" % (sum, one, two, three)
    print "第一天上涨的概率:%s,第二天上涨的概率:%s,第三天上涨的概率:%s" % (
        round(one / float(sum), 2), round(two / float(sum), 2), round(three / float(sum), 2))


def test(data):
    _data = StringUtils.str_2_arr(data['data'].splite(';'))
    SharesAnalyse.avgdif(_data)


if __name__ == '__main__':
    pass
