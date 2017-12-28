# coding:utf-8

# @author:apple
# @date:16/4/29
import numpy as np


def fit(data, n=16):
    """
    数据拟合 返回拟合函数
    :param data: 数据集合
    :param n: 拟合次数
    :return:
    """
    x = np.arange(0, len(data), 1)
    y = np.array(data)
    z1 = np.polyfit(x, y, n)
    return np.poly1d(z1)


def fit_deriv(data, n=16, m=1):
    """
    数据拟合 获取拟合后的导
    :param data: 数据集合
    :param n: 拟合次数
    :param m: 导数
    :return:
    """
    f = fit(data, n)
    return f.deriv(m=m)


def fit_root(data, n=16, m=1):
    """
    获取函数的根
    :param data:
    :param n:
    :param m:
    :return:
    """
    d = fit_deriv(data, n=n, m=m)
    r = np.roots(d)
    if len(r) < 2:
        new = n * 2
        return fit_root(data, n=new, m=m)
    return n


def fit_root_format_int(roots):
    """
    根格式化成int
    :param roots:
    :return:
    """
    res = []
    for i in range(len(roots)):
        res.append(int(np.real(roots[i])))
    return res


def fit_root_format_int_simple(roots, dif=6):
    """
    根格式化成int
    :param roots:
    :return:
    """
    res = []
    last = None
    for i in range(len(roots)):
        c = int(np.real(roots[i]))
        if last is not None:
            if last - c < dif:
                continue
        res.append(c)
        last = c
    res.reverse()
    return res


def fit_d_root_or_root_int_simple(data, n=16, m=1, dif=6):
    """
    获取导数root 以及两根之间的斜率
    :param data:
    :param n:
    :param m:
    :return:
    """
    d = fit_deriv(data, n=n, m=m)
    roots = np.roots(d)
    s_roots = fit_root_format_int_simple(roots, dif=dif)
    d_arr = []
    for i in range(len(s_roots) - 1):
        d_arr.append(round(d((s_roots[i] + s_roots[i + 1]) / 2), 3))
    return d_arr, s_roots


def normalization(data, zoom=100, offset=0):
    """
    线性归一化
    :param data:
    :param zoom: 放大倍数
    :param offset: 偏移量
    :return:
    """

    mi = min(data)
    dif = max(data) - mi
    res = []
    l = len(data)
    for i in range(l):
        res.append((data[i] - mi) / dif * zoom + offset)
    return res
