# coding:utf-8

# @author:apple
# @date:16/4/14
from flask import Blueprint
from web.ui import *
from web.busi.shares import *
from web.busi.StockService import *
from web.dataCenter.THSDataCenter import *
import time
import json

shares = Blueprint('shares', __name__,
                   template_folder='templates',
                   static_folder='static', url_prefix='/shares')


@shares.route('/getCurMinData', methods=['get', 'post'])
@json_view
def getCurMinData():
    args = request.args
    if request.method == 'POST':
        args = request.form
    code = args['code']
    share = Shares()
    a = json.loads(share.getMinDataByCode(code))
    b = a['data'][code]['data']['data']
    t = [0 for x in range(0, len(b))]
    price = [0 for x in range(0, len(b))]
    reuslt = {'time': t, 'price': price}

    for i in range(0, len(b)):
        arr = b[i].split(' ', 3)
        t[i] = arr[0]
        price[i] = arr[1]
    mx = float(max(price))
    mi = float(min(price))
    qt = a['data'][code]['qt']
    # 昨收
    zs_price = float(qt[code][4])
    # 涨幅额
    change = float(qt[code][31])
    # 涨幅
    chg = float(qt[code][32])
    # 最大价格
    max_price = float(qt[code][33])
    # 最低价格
    min_price = float(qt[code][34])
    c_price = max(max_price - zs_price, zs_price - min_price)
    print max_price, zs_price, max_price - zs_price
    reuslt['max'] = zs_price + c_price * 0.01 + c_price
    reuslt['min'] = zs_price - c_price - c_price * 0.01
    reuslt['zs_price'] = zs_price

    return reuslt


@shares.route('/getData', methods=['get', 'post'])
def getData():
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    share = Shares()
    share.downloadExcelFile()
    share.getMinData(date, '沪市(A)', 'sha')
    share.getMinData(date, '深市(A)', 'sza')
    share.getMinData(date, '创业板', 'cy')
    share.getMinData(date, '中小板', 'zxb')
    return render_template('html/index.html', name='开始获取当日数据....')


def selectShares():
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    # Shares().downloadExcelFile()
    list = Shares().getExcelData(date, "沪深(A)")
    client = WebClient()
    for i in range(1, len(list) - 1):
        code = list[i][0]
        data = SharesAnalyse.getDayData(code=list[i][0])
        if data is None:
            continue
        dlen = data['num']
        arr = [0 for x in range(0, dlen)]
        harr = [0 for x in range(0, dlen)]
        strs = data['data'].split(';', dlen)
        for i in range(0, dlen):
            s = strs[i].split(',', 8)
            if len(s) > 4 and StringUtils.isNum(s[4]) and s[4] != '':
                try:
                    arr[i] = float(s[4])
                    harr[i] = float(s[7])
                except Exception, e:
                    print e, strs[i]
                    continue
        a = SharesAnalyse.avgdif(arr)
        alen = len(a)
        if alen > 4:
            c = a[alen - 1]
            p = a[alen - 2]
            p1 = a[alen - 3]
            p2 = a[alen - 4]
            p3 = a[alen - 5]
            if c > p and p < 0 and c < p and p1 < 0 and p2 < 0 and p3 < 0 and p < p1 and p1 < p2:
                cdata = SharesAnalyse.getCurShareData(code=code, client=client)

                if cdata:
                    hpre = round(cdata['hs'] / harr[alen - 1], 2)
                    if (hpre < 0.5 or hpre > 2) and cdata['zf'] >= 0:
                        k = SharesAnalyse.Ktype(cur=cdata['cur'], openp=cdata['op'], hp=cdata['hp'], lp=cdata['lp'])
                        print "昨换:%s 今换:%s" % (harr[alen - 1], cdata['hs'])
                        print "代码: %s,当前价格: %s ,昨收: %s ,昨日5日线 %s " \
                              ",今日五日线: %s ,k线形态: %s ,涨幅: %s ,换手: %s ,换手比:%s" % (
                                  code, cdata['cur'], cdata['zs'], p, c, k, cdata['zf'], cdata['hs'], hpre)

    print '完成'


@shares.route('/getCurStockData', methods=['get', 'post'])
@json_view
def getCurStockData():
    args = request.args
    if request.method == 'POST':
        args = request.form
    code = args['code']
    return THSData().getStockLast(code)

@shares.route('/getCurStock', methods=['get', 'post'])
@json_view
def getCurStock():
    args = request.args
    if request.method == 'POST':
        args = request.form
    code = args['code']
    return THSData().getStockPlateInfoByCode(code)

@shares.route('/aysPublicData', methods=['get', 'post'])
@json_view
def aysPublicData():
    """
    分析发行数据
    :return:
    """
    return StockService().getCurYearPublicList()

@shares.route('/lastNewStockList', methods=['get', 'post'])
@json_view
def lastNewStockList():
    """
    获取开盘后的前七天数据
    :return:
    """
    return StockService().getLastNewStockData()


@shares.route('/b', methods=['get', 'post'])
@json_view
def stockBuy():
    """
    获取购买stock数据
    :return:
    """
    return StockService().get_stock_buy_data()


@shares.route('/plate', methods=['get', 'post'])
@json_view
def plate():
    """
    获取购买stock数据
    :return:
    """
    args = request.args
    if request.method == 'POST':
        args = request.form
    return StockService().get_plate(args)


@shares.route('/stockSearch', methods=['get', 'post'])
@json_view
def stockSearch():
    """
    获取购买stock数据
    :return:
    """
    args = request.args
    if request.method == 'POST':
        args = request.form

    plate=[]
    if args['area']:
        plate.extend( args['area'].split(","))
    if args['concept']:
        plate.extend( args['concept'].split(","))

    params={}
    for a in args:
        params[a]=args[a]
    params['plate'] = plate
    data = StockService().search(params)
    return data
