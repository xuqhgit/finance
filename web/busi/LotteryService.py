# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2017/2/15
from web.db.dbexec import DBExec
import LotteryAnalysis
LOTTERY_QUERY_PATH = 'query/LOTTERY.xml'
class LotteryService():
    """
    lottery 服务类
    """
    def getAllSsqData(self):
        db = DBExec(LOTTERY_QUERY_PATH, "GET_ALL_SSQ")
        data_list = db.execute(None)


        result = []
        for d in data_list:
            child = [int(d['main_num']),d['one']%16,d['two']%16,d['three']%16,d['four']%16,d['five']%16,d['six']%16,int(d['periods'][4:])%16,int(d['lottery_date'][8:])%16]

            for i in range(0,len(child)):
                if child[i] == 0:
                    child[i] = 16

            result.append(child)

        analysis = LotteryAnalysis.LotteryAnalysis()
        rs_list = analysis.mainNumAnalysis(result[len(result) - 11:])
        print sum(rs_list), len(rs_list), 1 - (sum(rs_list) * 1.0 / len(rs_list))




if __name__ == "__main__":
   lottery = LotteryService()
   lottery.getAllSsqData()
