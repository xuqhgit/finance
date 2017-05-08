# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2017/2/15

class LotteryAnalysis:
    """
    lottery 数据分析类
    """
    def mainNumAnalysis(self,data,step=1):
        """
        分析主号码发生概率
        :param data: 数据列表 格式为 [a,b...]
        :param step: 分析步数
        :return:
        """
        result = []
        for i in range(0+step,len(data)):
            num = data[i][0]
            cur_list = []
            [cur_list.extend(j) for j in data[i-step:i]]
            cur_data = set(cur_list)
            print num,cur_data,num in cur_data and 1 or 0,"len: %s" % len(cur_data)
            result.append(num in cur_data and 1 or 0)
        return result


