# coding:utf-8

from web.utils import FileUtils
from web.utils.FileUtils import FileUtils
import json
from web.db import MongoDBClient
from web.dataCenter import THSDataCenter
import logging
from threading import Thread
import os


_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# shares文件夹
json_path = os.path.join(_dir, 'static/file/json.json')


def load_redis_json_file():
    str = FileUtils.get_file(json_path)
    if str is None:
        logging.info("str is None")
        return
    logging.info("load json success")
    # json_arr = str.split('\",', 30100)
    # json_arr[0] = json_arr[0][2:]
    # last_str = json_arr[len(json_arr) - 1]
    # json_arr[len(json_arr) - 1] = last_str[0:-3]
    list = json.loads(str)
    size = len(list)
    logging.info("size:%s" % size)
    list_len = 500
    count = size / list_len + (size % list_len == 0 and 0 or 1)
    thread_list = []
    result = None
    logging.info("开启线程数:%s" % count)

    for i in range(0, count):
        if i == count - 1:
            t = Thread(target=save_data_2_mongo, args=(list[i * list_len:], result))
            t.start()
            break
        else:
            t = Thread(target=save_data_2_mongo,
                       args=(list[(i * list_len):((i + 1) * list_len)], result))
            t.start()
        thread_list.append(t)
    str = None
    for t in thread_list:
        t.join()
    logging.info("线程数 %s 执行完成" % count)


def save_data_2_mongo(list, result):
    for json_obj in list:
        # str = "{" + str + "\"}"
        # json_obj = json.loads(str)
        for k in json_obj:
            arr = k.split(":", 6)
            col = None
            date = "%s%s%s" % (arr[1], arr[2], arr[3])
            code = arr[5]
            id = "%s_%s_%s" % (arr[4], date, code)
            data = {'code': code, 'date': date, 'type': arr[4], 'data': json_obj[k]}
            if arr[4] == 'MONEY':
                col = THSDataCenter.MONGO_COL_MONEY_MIN
            elif arr[4] == 'LAST':
                col = THSDataCenter.MONGO_COL_LAST_MIN
            else:
                col = THSDataCenter.MONGO_COL_PLATE_MIN

            if col:
                try:
                    MongoDBClient.insert_json(id, data, col)
                except Exception, e:
                    logging.error(e)


if __name__ == '__main__':
    pass
    # load_redis_json_file()
