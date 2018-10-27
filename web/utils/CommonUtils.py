# -*- coding: utf-8 -*-
# author: apple
# createTime: 2016/11/6

from threading import Thread
import logging


def start_many_thread(list, handleSize=200, args=(), target=None, asyn=True, name='多线程任务'):
    """
    分批处理数据

    :param list: 处理数据集合
    :param handleSize: 单次大小
    :param args: 参数
    :param target: 处理函数
    :param asyn: 异步 默认为异步执行
    :param name: 任务名称
    :return:
    """

    if list is None:
        return 0
    size = len(list)
    list_len = handleSize
    count = size / list_len + (size % list_len == 0 and 2 or 3) - 2
    thread_list = []
    logging.info("【%s】 ->>>[__startManyThread] 开启线程数:%s 单个处理:%s 总处理:%s" % (name, count, list_len, size))
    for i in range(0, count):
        if i == count - 1:
            new_args = (list[i * list_len:],) + args
            t = Thread(target=target, args=new_args, name=i)
            t.start()
        else:
            new_args = (list[(i * list_len):((i + 1) * list_len)],) + args
            t = Thread(target=target, args=new_args, name=i)
            t.start()
        thread_list.append(t)
    if asyn is False:
        for t in thread_list:
            logging.info("【%s】 ->>>[__startManyThread] 线程名: %s 处理中..." % (name, t.getName()))
            t.join()
            logging.info("【%s】 ->>>[__startManyThread] 线程名: %s 处理完成..." % (name, t.getName()))
        logging.info("【%s】 ->>>[__startManyThread] 同步执行完成" % name)
    else:
        logging.info("【%s】 ->>>[__startManyThread] 正在处理中..." % name)
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
                result["%s" % i] = round(1 - float(j) / size, 4)
                break
            elif j + 1 == size:
                result["%s" % i] = 0
    return result
