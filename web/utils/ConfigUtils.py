# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2017/5/9
import ConfigParser

config_name = "config.conf"
cp = ConfigParser.SafeConfigParser()
cp.read(config_name)


def get(s, k):
    return cp.get(s, k)



