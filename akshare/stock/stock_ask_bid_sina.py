#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2024/10/05 22:00
Desc: 新浪-行情报价
https://finance.sina.com.cn/realstock/company/sz000001/nc.shtml
"""
from functools import lru_cache

import pandas as pd
import requests

import json
try:
    import re
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


INDEX_LABELS = ['sh', 'sz', 'hs300', 'sz50', 'cyb', 'zxb', 'zx300', 'zh500']
INDEX_LIST = {'sh': 'sh000001', 'sz': 'sz399001', 'hs300': 'sh000300',
              'sz50': 'sh000016', 'zxb': 'sz399005', 'cyb': 'sz399006', 
              'zx300': 'sz399008', 'zh500':'sh000905'}
LIVE_DATA_COLS = ['name', 'open', 'pre_close', 'price', 'high', 'low', 'bid', 'ask', 'volume', 'amount',
                  'buy_1_vol', 'buy_1', 'buy_2_vol', 'buy_2', 'buy_3_vol', 'buy_3', 'buy_4_vol', 'buy_4', 'buy_5_vol', 'buy_5',
                  'sell_1_vol', 'sell_1', 'sell_2_vol', 'sell_2', 'sell_3_vol', 'sell_3', 'sell_4_vol', 'sell_4', 'sell_5_vol', 'sell_5',
                  'date', 'time']

def _code_to_symbol(code):
    '''
        生成symbol代码标志
    '''
    if code in INDEX_LABELS:
        return INDEX_LIST[code]
    else:
        if len(code) != 6 :
            return code
        else:
            return 'sh%s'%code if code[:1] in ['5', '6', '9'] or code[:2] in ['11', '13'] else 'sz%s'%code
        
def _random(n=13):
    from random import randint
    start = 10**(n-1)
    end = (10**n)-1
    return str(randint(start, end))


def stock_bid_ask_sina(symbol: str = "000001") -> pd.DataFrame:
    """
        获取实时交易数据 getting real time quotes data
        用于跟踪交易情况（本次执行的结果-上一次执行的数据）
    Parameters
    ------
        symbol : string, array-like object (list, tuple, Series).
        
    return
    -------
        DataFrame 实时交易数据
        属性:0：name，股票名字
            1：open，今日开盘价
            2：pre_close，昨日收盘价
            3：price，当前价格
            4：high，今日最高价
            5：low，今日最低价
            6：bid，竞买价，即“买一”报价
            7：ask，竞卖价，即“卖一”报价
            8：volumn，成交量 maybe you need do volumn/100
            9：amount，成交金额（元 CNY）
            10：buy_1_vol，委买一（笔数 bid volumn）
            11：buy_1，委买一（价格 bid price）
            12：buy_2_vol，“买二”
            13：buy_2，“买二”
            14：buy_3_vol，“买三”
            15：buy_3，“买三”
            16：buy_4_vol，“买四”
            17：buy_4，“买四”
            18：buy_5_vol，“买五”
            19：buy_5，“买五”
            20：sell_1_vol，委卖一（笔数 ask volumn）
            21：sell_1，委卖一（价格 ask price）
            ...
            30：date_time，日期；
    """
    symbol = _code_to_symbol(symbol)
    zh_sina_stock_ask_bid_url = 'https://hq.sinajs.cn/rn={}&list={}'

    url = zh_sina_stock_ask_bid_url.format(_random(), symbol)
    r = requests.get(url, timeout=10, headers={
            'host': 'hq.sinajs.cn',
            'referer': 'https://finance.sina.com.cn/'
    })
    reg = re.compile(r'\="(.*?)\";')
    data = reg.findall(r.text)
    data_list = []
    for index, row in enumerate(data):
        if len(row)>1:
            data_list.append(astr for astr in row.split(',')[:32])

    df = pd.DataFrame(data_list, columns=LIVE_DATA_COLS)
    df['date_time'] = df['date'] + ' ' + df['time']
    df = df.drop(['date', 'time'], axis=1)
    df = df.apply(lambda x: round(float(x), 2) if (x.name != 'name' and x.name != 'date_time') else x)
    df = df.T.reset_index()
    df.columns = ["item", "value"]

    return df


if __name__ == "__main__":
    stock_bid_ask_sina = stock_bid_ask_sina(symbol="000001")
    print(stock_bid_ask_sina)