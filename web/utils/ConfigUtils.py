# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2017/5/9
import ConfigParser
from web.utils import FileUtils

config_name = "%s/%s/config.conf" % (FileUtils.web_dir, "utils")

cp = ConfigParser.SafeConfigParser()
cp.read(config_name)


def get(s, k):
    return cp.get(s, k)
