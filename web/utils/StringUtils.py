# coding:utf-8

# @author:apple
# @date:16/4/3
import random
import string
import datetime
import hashlib
import time
import re
import json

str = 'zyxwvutsrqponmlkjihgfedcba0123456789ZYXWVUTSRQPONMLKJIHGFEDCBA'


class StringUtils(object):
    """
        字符串工具类
    """

    def __init__(self):
        pass

    @staticmethod
    def get_random_string(self, count=5):
        """

        :rtype: object
        """
        return string.join(random.sample(str, count)).replace(" ", "")

    @staticmethod
    def get_token(type=0, timeout=9999, url=None):
        if url is None:
            token = "%s%s%04d%d%s" % (type, 0, timeout, int(time.time()), StringUtils.getRandomString(5))
        else:
            token = "%s%s%04d%s%s%s" % (type, 1, timeout, int(time.time()), StringUtils.getRandomString(5), url)
        m = hashlib.md5()
        m.update(token)
        entoken = m.hexdigest()
        return token, entoken

    @staticmethod
    def is_valid_token(token, entoken, url=None):
        m = hashlib.md5()
        m.update(token)
        _entoken = m.hexdigest()
        if _entoken == entoken:
            type = int(token[0:1])
            isUrl = int(token[1:2])
            timeout = int(token[2:6])
            timestamp = int(token[6:16])
            randomStr = token[16:21]
            if int(time.time()) - timestamp > timeout:
                return False, "token超时"
            if isUrl == 1:
                _url = token[21:len(token)]
                if _url != url:
                    return False, "非法的请求(T)"
            return True, "SUCESS"
        return False, "无效的TOKEN"

    @staticmethod
    def get_key(**param):
        str = ''
        for p in param:
            str += param[p]
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()

    @staticmethod
    def is_null(str):
        if str and str != '':
            return False
        return True

    @staticmethod
    def str_2_float(str):
        """
        字符串转float 如果为空 则返回0
        :param str: 转换的字符串
        :return: 返回相应的float
        """
        if StringUtils.is_null(str):
            return 0
        if str == "-":
            return 0
        return float(str)

    @staticmethod
    def is_num(num, minNum=None, maxNum=None):
        if StringUtils.is_null(num):
            return False, '请输入数字'
        r = re.compile(r'^\d*$').match(num)
        if r:
            if minNum is not None and int(num) < minNum:
                return False, '数值过小,请输入不小于%s' % minNum
            if maxNum is not None and int(num) > maxNum:
                return False, '数值过大,请输入不大于%s' % maxNum
            return True, ''
        return False, "数字格式不正确"

    @staticmethod
    def str_2_arr(data, spt=',', slen=-1):
        """
        特定的字符串进行切割转成相应的数组
        :param data: 切割数据
        :param spt: 分割符
        :param slen: 数组长度
        :return: 返回相应的数组
        """
        dlen = len(data)
        arr = []
        for i in range(0, dlen):
            s = data[i].split(spt, slen)
            l = len(s)
            if l > 0:
                a = []
                for j in range(0, l):
                    if s[j] and s[j] != '':
                        a.append(float(s[j]))
                    else:
                        a.append(0)
                if len(a) == l:
                    arr.append(a)
        return arr

    @staticmethod
    def str_2_json(jsonStr):
        """
        字符串转json
        :param jsonStr:
        :return:
        """
        if jsonStr:
            return json.loads(jsonStr)
        return None

    @staticmethod
    def json_2_str(data):
        """
        json 转字符串
        :param data:
        :return:
        """
        if isinstance(data, type(str)):
            return data
        else:
            return json.dumps(data)

    @staticmethod
    def stock_code_type(code):
        """

        :param code:
        :return:
        """
        code_type = None
        if code[0] == '6':
            code_type = 'sh'
        elif code[0] == '0':
            code_type = 'sz'
        elif code[0] == '3':
            code_type = 'cy'
        elif code[0] == '8':
            code_type = 'bk'
        return code_type


if __name__ == '__main__':
    a = ''
    print isinstance(a, type(str))
# 随机整数：
# print random.randint(1, 50)
# 随机选取0到100间的偶数：
# print random.randrange(0, 101, 2)
# 随机浮点数：
# print random.random()
# print random.uniform(1, 10)
# 随机字符：
# print random.choice('abcdefghijklmnopqrstuvwxyz!@#$%^&*()')
# 多个字符中选取特定数量的字符：
# print random.sample('', 5)
# 多个字符中选取特定数量的字符组成新字符串：
# print string.join(random.sample(
#         ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
#          'd', 'c', 'b', 'a'], 5)).replace(' ', '')
# 随机选取字符串：
# print random.choice(['剪刀', '石头', '布'])
# 打乱排序
# items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
# print random.shuffle(items)
