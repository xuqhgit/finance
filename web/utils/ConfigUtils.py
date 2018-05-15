# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2017/5/9
import ConfigParser
from web.utils import FileUtils
import logging

config_name = "%s/%s/config.conf" % (FileUtils.web_dir, "utils")

cp = ConfigParser.SafeConfigParser()
cp.read(config_name)


def get(s, k):
    return cp.get(s, k)


def get_val(s, k, default_val=None):
    try:
        return cp.get(s, k)
    except Exception, e:
        logging.error("获取配置文件值异常：%s" % e)
    return default_val
