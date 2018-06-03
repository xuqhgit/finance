# -*- coding: utf-8 -*-

import copy
import httplib
import json
import urllib
import urlparse
import logging
from bs4 import BeautifulSoup
import random
import re

ip_dict = {"list": []}


class CookieSet(object):
    def __init__(self, *args):
        self.d = {}
        if args:
            for line in args:
                if isinstance(line, dict):
                    self.d.update(line)
                elif isinstance(line, str):
                    self.parse_line(line)

    def parse_line(self, raw_line):
        lines = re.split(r'[\,]+', raw_line, re.I | re.S)
        for line in lines:
            pt = r'^([^\=]+)\=(.*)$'
            m = re.search(pt, line, re.I | re.S)
            if not m:
                continue
            key = urllib.unquote(m.group(1))
            raw_val = m.group(2)
            val_parts = re.split(r'[\;]+', raw_val)
            if val_parts:
                val = urllib.unquote(val_parts[0].strip())
            else:
                val = ''
            self.d[key] = val

    def _str(self, key, value):
        return key + '=' + value

    def to_str(self):
        return ','.join([self._str(k, self.d[k]) for k in self.d])

    def __repr__(self):
        return self.to_str()

    def get_dict(self):
        return copy.copy(self.d)

    def serialize(self):
        return json.dumps(self.d)

    def deserialize(self, data):
        d = json.loads(data)
        if d:
            self.d.update(d)


class Response(object):
    def __init__(self, raw_resp, cookies):
        self.status = raw_resp.status
        self.reason = raw_resp.reason
        self.headers = raw_resp.getheaders()
        self.data = raw_resp.read()
        if cookies:
            self.cookies = cookies.get_dict()

    def read(self):
        return self.data


class WebClient(object):
    def __init__(self, timeout=30, headers={}):
        self.cookies = {}
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        self.headers = headers

    def serialize(self):
        rows = [(k, self.cookies[k].serialize()) for k in self.cookies]
        return json.dumps(rows)

    def deserialize(self, data):
        rows = json.loads(data)
        rows = [(k, data, CookieSet()) for k, data in rows]
        for _, data, cook in rows:
            cook.deserialize(data)
        rows = [(k, cook) for k, _, cook in rows]
        self.cookies.update(dict(rows))

    def get(self, url, **kargs):
        return self.request('GET', url, None, **kargs)

    def post(self, url, data, **kargs):
        return self.request('POST', url, data, **kargs)

    def request(self, method, url, data,
                headers=None,
                auto_cookies=False,
                ajax=False,
                as_form=False):
        if headers:
            self.headers.update(headers)

        uri = urlparse.urlparse(url)
        netloc = uri.netloc

        if netloc not in self.cookies:
            self.cookies[netloc] = CookieSet()
        cook = self.cookies[netloc]

        conn = None
        scheme = uri.scheme.lower()

        if scheme == 'https':
            conn = httplib.HTTPSConnection(uri.hostname, uri.port or 443,
                                           timeout=self.timeout)
        else:
            conn = httplib.HTTPConnection(uri.hostname, uri.port or 80,
                                          timeout=self.timeout)
        _headers = {
            'user-agent': self.user_agent,

        }
        _headers.update(self.headers)
        if as_form and method.upper() == 'POST':
            keys = [k.lower() for k in _headers]
            if 'content-type' not in keys:
                _headers['content-type'] = 'application/x-www-form-urlencoded'
        if auto_cookies and cook:
            _headers['cookie'] = cook.to_str()
        if ajax:
            keys = [k.lower() for k in _headers]
            if 'x-requested-with' not in keys:
                _headers['X-Requested-With'] = 'XMLHttpRequest'
        _data = data
        if _data and isinstance(_data, dict):
            _data = urllib.urlencode(_data)
        _url = uri.path + '?' + uri.query if uri.query else uri.path

        # for d,x in _headers.items():
        # print "key:"+d+",value:"+str(x)

        conn.request(method, _url, _data, _headers)
        resp = conn.getresponse()
        if resp:
            headers = resp.getheaders()
            for key, val in headers:
                if key.lower() == 'set-cookie' and val:
                    # print 'set-cookie:', val
                    cook.parse_line(val)

        return Response(resp, cook)

    def load_proxy_id(self):
        """
        加载ip列表
        :return:
        """
        logging.info("加载代理服务器ip列表")
        url_1 = ["http://www.xicidaili.com/wt/", "http://www.xicidaili.com/nt/"][
            random.randint(0, 1)]
        resp = self.get(url_1)
        if resp.status == 200:
            ip_dict['list'] = []
            trs = BeautifulSoup(resp.data, "html.parser").find(id='ip_list').select("tr")
            for i in range(1, len(trs)):
                tr = trs[i]
                tds = tr.select('td')
                ip = str(tds[1].string.strip())
                port = int(tds[2].string.strip())
                ip_type = tds[4].string.strip()
                # if ip_type == u'透明':
                ip_dict['list'].append({"ip": ip, "port": port})

        else:
            logging.error("获取代理服务器数据错误：%s" % resp.status)
        return ip_dict['list']

    def get_ip(self):
        """
        获取ip列表
        :return:
        """
        if ip_dict['list']:
            return ip_dict['list'][0]
        ip_dict['list'].extend(self.load_proxy_id())
        if ip_dict['list']:
            return ip_dict['list'][0]
        logging.error("无法获取可用的proxy ip")
        return None

    def clear_ips(self):
        """
        清理ip列表
        :return:
        """
        ip_dict['list'] = []

    def ips_remove(self, x):
        """
        移除
        :return:
        """
        logging.info("移除proxy id %s " % json.dumps(x))
        try:
            ip_dict['list'].remove(x)
        except Exception, e:
            pass

    def proxy_get(self, url):
        ip = self.get_ip()
        conn = httplib.HTTPConnection(ip['ip'], ip['port'], timeout=self.timeout)
        try:
            conn.request('GET', url)
            r = conn.getresponse()
            if r.status != 200 or re.match(r'Unauthorized', r.read()) or bool(r.read()) is False:
                self.ips_remove(ip)
            return Response(r, self.cookies)
        except Exception, e:
            self.ips_remove(ip)
            return None


if __name__ == '__main__':
    client = WebClient()
    resp = client.get('http://fund.eastmoney.com/150092.html')
    print resp.data
    # print resp.read()

