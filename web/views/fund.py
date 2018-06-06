# coding:utf-8

# @author:apple
# @date:16/4/14
from flask import Blueprint
from web.busi.FundService import FundService

from web.ui import *

fund = Blueprint('fund', __name__,
                 template_folder='templates',
                 static_folder='static', url_prefix='/fund')


@fund.route('/fundListByStock', methods=['get', 'post'])
@json_view
def fundListByStock():
    """
    获取购买stock数据
    :return:
    """
    args = request.args
    if request.method == 'POST':
        args = request.form

    params = {}
    for a in args:
        params[a] = args[a]
    data = FundService().get_stock_fund(args['stock_code'])
    return data
