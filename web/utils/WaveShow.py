# -*- coding: utf-8 -*-
# author: Administrator
# createTime: 2017/5/9

import matplotlib.pyplot as plt
import numpy as np
from web.utils import FitFunction


def show(d, n=16, dif=3):
    data = d
    x = np.arange(0, len(data), 1)
    y = np.array(data)
    # 用n次多项式拟合
    z1 = np.polyfit(x, y, n)
    p1 = np.poly1d(z1)
    print(FitFunction.fit_d_root_or_root_int_simple(d, n=n, dif=dif))
    # 在屏幕上打印拟合多项式
    print(p1)
    # 也可以使用yvals=np.polyval(z1,x)
    yvals = p1(x)
    plot1 = plt.plot(x, y)
    plot2 = plt.plot(x, yvals)
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    # 指定legend的位置,读者可以自己help它的用法
    plt.legend(loc=4)
    plt.title('波形')
    plt.show()
    # 保存图片
    # plt.savefig('p1.png')
