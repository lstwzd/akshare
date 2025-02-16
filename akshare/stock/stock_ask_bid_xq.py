# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2024/10/6 01:30
Desc: 雪球-实时行情
https://xueqiu.com/S/SZ000001
"""
import re

import pandas as pd
import requests

from datetime import datetime

INDEX_LABELS = ['SH', 'SZ', 'HS300', 'SZ50', 'CYB', 'ZXB', 'ZX300', 'ZH500']
INDEX_LIST = {
    'SH': 'SH000001',
    'SZ': 'SZ399001',
    'HS300': 'SH000300',
    'SZ50': 'SH000016',
    'CYB': 'SZ399006',
    'ZXB': 'SZ399005',
    'ZX300': 'SZ399008',
    'ZH500': 'SH000905'
}

def _code_to_symbol(code):
    '''
        生成symbol代码标志
    '''
    if code in INDEX_LABELS:
        return INDEX_LIST[code]
    elif code[:3] == 'GB_':
        return code
    else:
        if len(code) != 6 :
            return code
        else:
            return 'SH%s'%code if code[:1] in ['5', '6', '9'] or code[:2] in ['11', '13'] else 'SZ%s'%code


def _convert_timestamp(timestamp_ms):
    """
    将以毫秒为单位的时间戳转换为日期和时间，并保留到秒。

    参数:
    timestamp_ms (int): 以毫秒为单位的时间戳

    返回:
    datetime: 对应的日期和时间，保留到秒
    """

    # 将毫秒转换为秒
    timestamp_s = timestamp_ms / 1000

    # 使用 fromtimestamp 方法将时间戳转换为 datetime 对象
    datetime_obj = datetime.fromtimestamp(timestamp_s)

    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")


def stock_bid_ask_xq(
        symbol: str = "SZ000001",
        timeout: float = None,
) -> pd.DataFrame:
    """
    雪球-行情中心-个股
    https://xueqiu.com/S/SZ000001
    :param symbol: 证券代码，可以是 A 股代码，A 股场内基金代码，A 股指数，美股代码, 美股指数
    :type symbol: str
    :param timeout: choice of None or a positive float number
    :type timeout: float
    :return: 证券最新行情
    :rtype: pandas.DataFrame
    """

    symbol = _code_to_symbol(symbol)

    session = requests.Session()
    headers = {
        "cookie": "xq_a_token=dbc1dc6d13bd101dd06f18c5b7f2fb2eb276fb5a;",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    }
    session.get(url="https://xueqiu.com", headers=headers)
    url = f"https://stock.xueqiu.com/v5/stock/realtime/pankou.json?symbol={symbol}"
    r = session.get(url, headers=headers, timeout=timeout)
    column_name_map = {
        "timestamp": "date_time",
        "bp1": "buy_1",
        "bc1": "buy_1_vol",
        "bp2": "buy_2",
        "bc2": "buy_2_vol",
        "bp3": "buy_3",
        "bc3": "buy_3_vol",
        "bp4": "buy_4",
        "bc4": "buy_4_vol",
        "bp5": "buy_5",
        "bc5": "buy_5_vol",
        "sp1": "sell_1",
        "sc1": "sell_1_vol",
        "sp2": "sell_2",
        "sc2": "sell_2_vol",
        "sp3": "sell_3",
        "sc3": "sell_3_vol",
        "sp4": "sell_4",
        "sc4": "sell_4_vol",
        "sp5": "sell_5",
        "sc5": "sell_5_vol",
        "current": "price",
    }
    json_data = r.json()["data"]
    temp_df = pd.json_normalize(json_data)
    temp_df = temp_df[column_name_map.keys()]
    temp_df.columns = [
        *map(
            lambda x: column_name_map[x] if x in column_name_map.keys() else x,
            temp_df.columns,
        )
    ]
    
    #保持与em, sina统一
    temp_df['bid'] = temp_df['buy_1']
    temp_df['ask'] = temp_df['sell_1']

    temp_df = temp_df.T.reset_index()
    temp_df.columns = ["item", "value"]
    temp_df.loc[temp_df["item"] == "date_time", "value"] = temp_df.loc[
        temp_df["item"] == "date_time", "value"
    ].apply(lambda x: _convert_timestamp(int(x)))

    return temp_df


if __name__ == "__main__":
    stock_ask_bid_xq_df = stock_bid_ask_xq(symbol="600036")
    print(stock_ask_bid_xq_df)
