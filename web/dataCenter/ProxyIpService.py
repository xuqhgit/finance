# -*- coding: utf-8 -*-

from web.utils import webclient
import logging
from bs4 import BeautifulSoup

ip_list = []


class ProxyService(object):
    """
    代理服务
    """

    def load_proxy_id(self):
        url_1 = "http://www.xicidaili.com/wt/"
        client = webclient.WebClient()
        resp = client.get(url_1)
        if resp.status == 200:
            ip_list = []
            trs = BeautifulSoup(resp.data, "html.parser").find(id='ip_list').select("tr")
            for i in range(1, len(trs)):
                tr = trs[i]
                tds = tr.select('td')
                ip = str(tds[1].string.strip())
                port = int(tds[2].string.strip())
                ip_list.append({"ip": ip, "port": port})
        else:
            logging.error("获取代理服务器数据错误：%s" % resp.status)
        print ip_list


if __name__ == '__main__':
    ps = ProxyService()
    ps.load_proxy_id()
