# coding:utf-8

# @author:apple
# @date:16/4/3
import random
import string
import hashlib
import time
import re
import json

RANDOM_STR = 'zyxwvutsrqponmlkjihgfedcba0123456789ZYXWVUTSRQPONMLKJIHGFEDCBA'


def get_random_string(count=5):
    """

    :rtype: object
    """
    return string.join(random.sample(RANDOM_STR, count)).replace(" ", "")


def get_token(type=0, timeout=9999, url=None):
    if url is None:
        token = "%s%s%04d%d%s" % (type, 0, timeout, int(time.time()), get_random_string(5))
    else:
        token = "%s%s%04d%s%s%s" % (type, 1, timeout, int(time.time()), get_random_string(5), url)
    m = hashlib.md5()
    m.update(token)
    entoken = m.hexdigest()
    return token, entoken


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


def get_key(**param):
    str = ''
    for p in param:
        str += param[p]
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()


def is_null(str):
    if str and str != '':
        return False
    return True


def str_2_float(str):
    """
    字符串转float 如果为空 则返回0
    :param str: 转换的字符串
    :return: 返回相应的float
    """
    if is_null(str):
        return 0
    if str == "-":
        return 0
    return float(str)


def is_num(num, minNum=None, maxNum=None):
    if is_null(num):
        return False, '请输入数字'
    r = re.compile(r'^\d*$').match(num)
    if r:
        if minNum is not None and int(num) < minNum:
            return False, '数值过小,请输入不小于%s' % minNum
        if maxNum is not None and int(num) > maxNum:
            return False, '数值过大,请输入不大于%s' % maxNum
        return True, ''
    return False, "数字格式不正确"


def str_2_arr(data, spt=',', slen=-1):
    """
    特定的字符串进行切割转成相应的数组 数据转换成 float
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

                    if s[j].find('.') > -1:
                        a.append(float(s[j]))
                    else:
                        a.append(int(s[j]))
                else:
                    a.append(0)
            if len(a) == l:
                arr.append(a)
    return arr


def str_2_json(jsonStr):
    """
    字符串转json
    :param jsonStr:
    :return:
    """
    if jsonStr:
        return json.loads(jsonStr)
    return None


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


def stock_code_type(code):
    """
    根据stock代码 获取stock类型
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
    elif code[0:2] == '1A':
        code_type = 'm'
    else:
        code_type = 'qt'
    return code_type


def stock_code_type_int(code):
    """
    根据stock代码 获取stock类型 1 2 3
    :param code:
    :return:
    """
    code_type = None
    if code[0] == '6':
        code_type = '1'
    elif code[0] == '0':
        code_type = '2'
    elif code[0] == '3':
        code_type = '3'
    return code_type


def str_remove_point_int(s):
    """
    字符串去掉小数点转int
    :param s:
    :return:
    """
    return int(s.replace(".", ""))


def arr_str_remove_point_int(arr):
    res = []
    for i in range(len(arr)):
        res.append(str_remove_point_int(arr[i]))
    return


def arr_str_float(arr):
    """
    数组字符串转数组float
    :param arr:
    :return:
    """
    res = []
    for i in range(len(arr)):
        res.append(float(arr[i]))
    return


def handle_ths_str_data_to_list(data):
    return str_2_arr(data.split(";"))


def arr_multiply_2_int(arr, m=100):
    result = []
    for i in range(len(arr)):
        result.append(int(arr[i] * m))
    return result


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
