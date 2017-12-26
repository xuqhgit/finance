# coding:utf-8

# @author:apple
# @date:16/1/18
import execjs

import FileUtils
"""
该方法为调用同花顺的的token值
"""
e = execjs.compile(open(r"%sths_v.js" % FileUtils._static_components_path).read().decode("utf-8"))


def get_v():
    return e.call('getV')
