# -*- coding: utf-8 -*-
# author: apple
# createTime: 2016/11/6

from threading import Thread
import logging


def start_many_thread(list, handleSize=200, result=None, target=None, asyn=False):
    """
    分批处理数据
    :param handleSize:
    :param result:
    :param target:
    :return:
    """
    size = len(list)
    list_len = handleSize
    if size > 6000:
        list_len = 300
    count = size / list_len + (size % list_len == 0 and 0 or 1)
    thread_list = []

    for i in range(0, count):
        if i == count - 1:
            t = Thread(target=target, args=(list[i * list_len:], result))
            t.start()
        else:
            t = Thread(target=target, args=(list[(i * list_len):((i + 1) * list_len)], result))
            t.start()
        thread_list.append(t)
    if asyn is False:
        for t in thread_list:
            t.join()
        logging.info("[__startManyThread] 同步执行")
    logging.info("[__startManyThread] 开启线程数:%s" % len(thread_list))
    return len(thread_list)


def calculateLgProArray(list, lg):
    """
    计算 集合[1,2,3,4,5,7] 中 大于[2,3] 概率
    :param list:
    :param lg:
    :return:
    """
    list.sort()
    size = len(list)
    result = {}
    for i in lg:
        for j in range(0, size):
            if i <= list[j]:
                result["%s" % i] = round(1-float(j) / size, 4)
                break
            elif j + 1 == size:
                result["%s" % i] = 0
    return result

