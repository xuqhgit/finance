# -*- coding: utf-8 -*-
# author: apple
# createTime: 2016/10/26


from web.utils import StringUtils
from web.utils import CommonUtils
from web.dataCenter import StockData
import numpy
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
            # print "%s=%s - %s" % (r, s, pres)
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
                # print suma / (suma + sumb)
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
        获取平均值 均线
        :param data: list类型数据 每日收盘price集合
        :param avg: 平均数分母大小 5 10 20 分别对应5日 10日
        :param r: 小数点长度
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
                return '+'
        # 无上影线下影线
        if upDif == 0 and downDif == 0:
            return 'C'
        # 无上影线
        if upDif == 0:
            if downDif / abs(midDif) >= 2:
                # 锤子
                return 'q'
            else:
                return 'p'
        # 无下影线
        if downDif == 0:
            if upDif / abs(midDif) >= 2:
                # 锤子
                return 'd'
            else:
                return 'b'

        upPre = upDif / maxDif
        downPre = downDif / maxDif
        midPre = abs(midDif) / maxDif
        preDif = upPre - downPre
        absPreDif = abs(preDif)
        if midPre <= 0.15:
            if absPreDif <= 0.1:
                return "+"
            return preDif > 0 and "L" or "T"
        elif 0.15 < midPre <= 0.33:
            if absPreDif > 0.1:
                return preDif > 0 and "d" or "q"
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
        :param data: list长度[[时间，开，高，低，收，量，额，换]]
        :param tc: 默认周期为 9日 与同花顺一致
        :return:
        """
        dlen = len(data)
        arr = data
        # 默认k值
        k = 50
        # 默认d值
        d = 50
        result = []
        for i in range(0, dlen):
            a = arr[tc <= i + 1 and i + 1 - tc or 0:i + 1]
            h = a[:, 2].max()
            l = a[:, 3].min()
            c = arr[i, 4]
            rsv = (c - l) / (h - l) * 100
            k = rsv / 3 + 2 * k / 3
            d = k / 3 + 2 * d / 3
            j = 3 * k - 2 * d
            result.append([int(arr[i, 0]), round(k, 2), round(d, 2), round(j, 2)])
        return result

    @staticmethod
    def getBias(data, tc=[6]):
        """
        bias数据
        :param data: 同kdj
        :param tc: 周期
        :return:
        """
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
        """
        boll数据
        :param data: 同kdj
        :param d:
        :return:
        """
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
        arr.append(r)
        return arr

    @staticmethod
    def getMacd(data, avga=12, avgb=26, avgc=9):
        """
        macd 指数数据
        :param data:
        :param avga:
        :param avgb:
        :param avgc:
        :return:
        """
        dlen = len(data)
        a = 0
        b = 0
        c = 0
        result = []
        # aArr = []
        # bArr = []
        for i in range(1, dlen):
            if i != 1:
                a = (a * (avga - 1) / (avga + 1)) + (2 * data[i] / (avga + 1))
                b = (b * (avgb - 1) / (avgb + 1)) + (2 * data[i] / (avgb + 1))
            else:
                a = data[i - 1] + (data[i] - data[i - 1]) * 2 / (avga + 1)
                b = data[i - 1] + (data[i] - data[i - 1]) * 2 / (avgb + 1)

            dif = round(a - b, 4)

            c = (c * (avgc - 1) / (avgc + 1)) + (2 * dif / (avgc + 1))

            result.append([round(((dif - c) * 2), 2), round(dif, 2), round(c, 2)])

        # dif = numpy.array(aArr) - numpy.array(bArr)

        return result


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


def analysisAvgLast(code, year='last', type='01', avg=[5, 10, 20]):
    """
    分析日线 最近的数据
    :param code:
    :return:
    """
    import StockService
    from web.utils import FitFunction
    data = StockService.StockService().getStockHistoryData(code, year=year, type=type)
    arr = StringUtils.handle_ths_str_data_to_list(data['data'])
    d = numpy.array(arr)[:, 4]
    avg_arr = numpy.array(CommonAnalysis.getAvgData(d, avg=avg))
    result = {}
    for i in range(len(avg)):
        a = numpy.array(avg_arr)[:, i]
        d, r = FitFunction.fit_d_root_or_root_int_simple(a)
        result[avg[i]] = {'d': d, 'r': r, 'a': a[len(a) - 10:]}
    return result


def analysis(param, codeList=[]):
    """
    数据分析
    :param param:
    :return:
    """
    # 日属性
    # param[''] = None
    # 值为 * 占位表示任意
    # xt：形态
    # k：高开h 低l 持平e  （在百分比为0.005为界限划分）
    # rg：收红还是收绿 红 r  绿g
    # zd: 涨z 跌d 相对昨天涨跌
    # hs: 相对换手率 相对昨天几倍 数值型 0 0.5 1 2 3 4 一位小数点
    stock_property = {'xt': ['+'], 'k': '*', 'rg': '*', 'zd': '*', 'hs': ''}
    stock_property_arr = [{'xt': ['T', 'q', 'p'], 'k': '*', 'rg': '*', 'zd': '*', 'hs': ''}, stock_property]
    stock_property_arr_len = len(stock_property_arr)
    pro_index = 9
    for i in range(len(codeList)):
        handle_data = handle_stock_daily_data(codeList[i])
        if handle_data is None:
            continue
        handle_data_len = len(handle_data)
        for j in range(handle_data_len):

            for k in range(stock_property_arr_len):
                prop = stock_property_arr[k]
                if j + k >= handle_data_len:
                    logging.info("匹配数据超出数据长度...")
                    break
                stock_data = handle_data[j + k][pro_index]
                if (prop['xt'] == '*' or prop['xt'] == stock_data['xt'] or stock_data['xt'] in prop['xt']) is False:
                    break
                if (prop['k'] == '*' or prop['k'] == stock_data['k'] or stock_data['k'] in prop['k']) is False:
                    break
                if (prop['rg'] == '*' or prop['rg'] == stock_data['rg'] or stock_data['rg'] in prop['rg']) is False:
                    break
                if (prop['zd'] == '*' or prop['zd'] == stock_data['zd'] or stock_data['zd'] in prop['zd']) is False:
                    break
                if k + 1 == stock_property_arr_len:
                    # 匹配
                    logging.info("数据匹配成功")
                    r = handle_data[j + k:handle_data_len - j - k > 10 and j + k + 10 or handle_data_len]
                    if len(r) > 0:
                        close_price = r[0]['data'][4]
                        temp_result = []
                        for m in range(1, len(r)):
                            c_price_pre = round((r[m]['data'][4] - close_price) / close_price, 2)
                            r[m]['xdzf'] = c_price_pre
                            temp_result.append(c_price_pre)
                        logging.info(temp_result)
    return None


def handle_stock_daily_data(code, avg=[5]):
    """
    将stock日数据进行解析 得出相应的数据
    :param code:
    :return:
    """
    data = StockData.get_stock_last_day(code)
    if bool(data) is False:
        return None
    kdj_result = CommonAnalysis.getKDJ(numpy.array(data))
    avg_result = CommonAnalysis.getAvgData(numpy.array(data)[:, 4], avg=avg)
    macd_result = CommonAnalysis.getMacd(numpy.array(data)[:, 4])
    rsi_result = CommonAnalysis.getrsi(data)
    print avg_result
    # boll_result = CommonAnalysis.getBoll(numpy.array(data)[:, 4])
    result = []
    for i in range(1, len(data)):
        pre = data[i - 1]
        cur = data[i]
        xt = CommonAnalysis.Ktype(cur=cur[4], openp=cur[1], hp=cur[2], lp=cur[3])
        k = pre[4] - cur[1] > 0 and 'l' or 'h'
        rg = cur[1] - cur[4] > 0 and 'g' or 'r'
        zd = pre[4] - cur[4] > 0 and 'd' or 'z'
        # TODO 换手率暂时不做计算

        r = {'xt': xt, 'k': k, 'rg': rg, 'zd': zd, 'data': cur, 'kdj': kdj_result[i], 'avg': avg_result[i],
             'macd': macd_result[i - 1], 'rsi': rsi_result[i - 1]}
        result.append(r)
    return result


def get_avg(code, data=[], avg=[5]):
    """
    获取日线数据
    :param code:
    :return:
    """
    data = bool(data) and data or StockData.get_stock_last_day(code)

    avg_result = CommonAnalysis.getAvgData(numpy.array(data)[:, 4], avg=avg)

    avg_len = len(avg_result)
    data_len = len(data)
    for i in range(avg_len):
        data[data_len - i - 1].append(avg_result[data_len - i - 1])
    for i in range(0, data_len - avg_len):
        data[i] = []
    return data


def get_boll(code, data=[], d=20):
    """
    获取boll数据
    :param code:
    :return:
    """
    data = bool(data) and data or StockData.get_stock_last_day(code)

    boll_result = CommonAnalysis.getBoll(numpy.array(data)[:, 4], d=d)

    boll_len = len(boll_result)
    data_len = len(data)
    for i in range(boll_len):
        data[data_len - i - 1].append(boll_result[data_len - i - 1])
    for i in range(0, data_len - boll_len):
        data[i] = []
    return data


def get_kdj(code, data=[], tc=9):
    """
    获取 kdj
    :param code:
    :return:
    """
    data = bool(data) and data or StockData.get_stock_last_day(code)

    kdj_result = CommonAnalysis.getKDJ(numpy.array(data), tc=tc)

    kdj_len = len(kdj_result)
    data_len = len(data)
    for i in range(kdj_len):
        data[data_len - i - 1].append(kdj_result[data_len - i - 1])
    for i in range(0, data_len - kdj_len):
        data[i] = []
    return data


def get_macd(code, data=[], avga=12, avgb=26, avgc=9):
    """
    获取 macd
    :param code:
    :return:
    """
    data = bool(data) and data or StockData.get_stock_last_day(code)
    macd_result = CommonAnalysis.getMacd(numpy.array(data)[:, 4], avga=avga, avgb=avgb, avgc=avgc)
    macd_len = len(macd_result)
    data_len = len(data)
    for i in range(macd_len):
        data[data_len - i - 1].append(macd_result[data_len - i - 1])
    for i in range(0, data_len - macd_len):
        data[i] = []
    return data


def get_rsi(code, data=[], avg=6, r=2):
    """
    获取 rsi
    :param code:
    :return:
    """
    data = bool(data) and data or StockData.get_stock_last_day(code)
    rsi_result = CommonAnalysis.getrsi(numpy.array(data), avg=avg, r=r)
    rsi_len = len(rsi_result)
    data_len = len(data)
    for i in range(rsi_len):
        data[data_len - i - 1].append(rsi_result[data_len - i - 1])
    for i in range(0, data_len - rsi_len):
        data[i] = []
    return data


def growth_Analysis(data_list, avgs=[5]):
    """
    计算涨幅
    :param data_list:
    :param avg:
    :return:
    """
    result = []
    for a in range(0, len(avgs)):
        avg = avgs[a]
        avg = avg + 1
        if len(data_list) < avg:
            avg = len(data_list)
        n_data_list = data_list[len(data_list) - avg:]
        growth = []
        change = []
        volumn = []
        last_price = n_data_list[0][4]
        last_change = n_data_list[0][7]
        for i in range(1, len(n_data_list)):
            if last_change == 0:
                last_change = 1
            growth.append(round((n_data_list[i][4] - last_price) * 100 / last_price, 3))
            last_price = n_data_list[i][4]
            change.append(round((n_data_list[i][7] - last_change) * 100 / last_change, 3))
            last_change = n_data_list[i][7]

            avg_val = round(numpy.mean(growth), 3)
            chg_avg_al = round(numpy.mean(change), 3)

        result.append(
            [avgs[a], avg_val, round(numpy.std(growth, ddof=1), 3), chg_avg_al, round(numpy.std(change, ddof=1), 3),
             change[len(change)-1]])
    return result

if __name__ == '__main__':
    # print handle_stock_daily_data("601838", avg=[5, 10, 20, 30, 60])
    # print growth_Analysis([-1.23, 1, 1.2, 1.3, 1.6])
    print
    # l = [[1, 3, 4, {'a': [1, 2, 3]}], [9, 4, 6, {'a': [1, 2, 3]}]]
    # #
    # print numpy.array(l)[:, 1]





    # ----------画图------------

    # from web.dataCenter.THSDataCenter import THSData
    #
    # import StockService
    #
    # center = THSData()
    #
    # data = StockService.StockService().getStockHistoryData("601108", "last", "01")
    # arr = StringUtils.handle_ths_str_data_to_list(data['data'])
    # d = numpy.array(arr)[:, 4]
    # avg_arr = numpy.array(CommonAnalysis.getAvgData(d, avg=[3]))
    # # print numpy.array(avg_arr)[:, 0]
    # from web.utils import WaveShow
    # a = avg_arr[:, 0]
    # for i in range(0, 5):
    #     f = 30 + (i * 5)
    #     t = 60 + (i * 5)
    #
    #     WaveShow.show(numpy.array(a[f:t]), n=8)





    # if __name__ == '__main__':
    #     data = StockService.StockService().getStockHistoryData("600926", "2017", "01")
    #     arr = StringUtils.str_2_arr(data['data'].split(";"))
    #     print BusinessAnalysis.analysisPublicData([{'data': arr}])
