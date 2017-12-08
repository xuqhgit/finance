# coding:utf-8

# @author:apple
# @date:16/1/18
import execjs

import FileUtils

e = execjs.compile(open(r"%sths_v.js" % FileUtils._static_components_path).read().decode("utf-8"))


def get_v():
    return e.call('getV')
