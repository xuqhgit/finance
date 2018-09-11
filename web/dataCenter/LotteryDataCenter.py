# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2017/8/15
from web.utils.webclient import WebClient
import logging
import xml.dom.minidom
from web.utils import StringUtils
class LotteryDataCenter(object):

    def download_gd_115(self, date):
        """
        :param date:
        :return:
        """

        client = WebClient()
        url = "http://kaijiang.500.com/static/info/kaijiang/xml/gdsyxw/%s.xml?_A=NPDYUKTS1502783714817" % date
        data = client.get(url)
        list = []
        if data.status == 200:
            str = data.data.decode('gb2312').encode('utf-8'),
            str = str[0].replace('gb2312', 'utf-8')
            d = xml.dom.minidom.parseString(str)

            elements = d.documentElement.getElementsByTagName("row")

            for element in elements:
                json = {'code':int(element.getAttribute('expect').replace("-","")),'open_time':element.getAttribute('opentime'),'result':element.getAttribute('opencode')}
                list.append(json)
            pass
        else:
            logging.error("500网下载广东11选5出错:%s" % data.status)
            return
        return list

