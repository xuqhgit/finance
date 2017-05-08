# -*- coding: utf-8 -*-
# author: apple
# createTime: 2016/10/26


from web.utils.StringUtils import StringUtils
from web.utils import CommonUtils
import json
import os
import time
import thread
import logging
import numpy
import StockService
import logging


class CommonAnalysis(object):
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
        """

        :param data:
        :param avga:
        :param avgb:
        :return:
        """
        if avga >= avgb:
            return None
        a = CommonAnalysis.getAvgData(data, avg=[avga, avgb])
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


class BusinessAnalysis(object):
    """
    业务数据分析
    """

    @staticmethod
    def analysisPublicData(list):
        """
        分析stock 发行数据
        :param list: [{'code':603999,'data':[]}]
        :return:
        """

        fist = []
        second = []
        third = []
        fourth = []
        fifth = []
        five_data = {"0": fist, "1": second, "2": third, '3': fourth, '4': fifth}
        result = {}

        for item in list:
            data = item['data']
            item['size'] = len(data)

            for i in range(2, item['size']):
                cur = data[i]
                if cur[1] != cur[2] or cur[1] != cur[3]:
                    item['count'] = i - 1
                    pre = data[i - 1]
                    for j in range(i, i + 5):

                        if j < item['size']:
                            cur = data[j]
                            pre_close = pre[4]
                            open = round((cur[1] - pre_close) * 100 / pre_close, 3)
                            high = round((cur[2] - pre_close) * 100 / pre_close, 3)
                            low = round((cur[3] - pre_close) * 100 / pre_close, 3)
                            close = round((cur[4] - pre_close) * 100 / pre_close, 3)
                            low_close = round((cur[4] - cur[3]) * 100 / pre_close, 3)
                            open_close = round((cur[4] - cur[1]) * 100 / pre_close, 3)
                            five_data['%s' % (j - i)].append([open, high, low, close, low_close, open_close])
                        else:
                            # r_df.append([-100, -100, -100, -100])
                            pass

                    break
        lg = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for i in five_data:
            a = numpy.array(five_data[i])
            result[i] = {}
            if len(a) is 0:
                continue
            for j in range(0, 6):
                b = a[:, j]
                c = {"avg": round(b.mean(), 3), "max": round(b.max(), 3), "min": round(b.min(), 3),
                     "s2": round(b.var(), 3), "count": len(b), 'pro': CommonUtils.calculateLgProArray(b, lg)}
                result[i]['%s' % j] = c
        return result


# if __name__ == '__main__':
#     data = StockService.StockService().getStockHistoryData("603999", "2016", "01")
#     arr = StringUtils.str_2_arr(data['data'].split(";"))
#     d = numpy.array(arr)[:, 4]
#     avg_arr = numpy.array(CommonAnalysis.getAvgData(d, avg=[3, 5, 7, 10, 20, 30]))
#
#     result = avg_arr[-10:, 0:4] - avg_arr[-10:, 1:5]
#     print result

if __name__ == '__main__':
    data = StockService.StockService().getStockHistoryData("600926", "2016", "01")
    arr = StringUtils.str_2_arr(data['data'].split(";"))
    print BusinessAnalysis.analysisPublicData([{'data': arr}])
