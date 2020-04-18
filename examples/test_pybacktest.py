
from __future__ import print_function

import pybacktest  # obviously, you should install pybacktest before importing it
import baostock as bs
import pandas as pd

def test_1():
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    # print('login respond error_code:' + lg.error_code)
    # print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    rs = bs.query_history_k_data_plus("sz.000001",
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date='2018-04-01', end_date='2020-04-18',
                                      frequency="d", adjustflag="3")
    # print('query_history_k_data_plus respond error_code:' + rs.error_code)
    # print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####
    # result.to_csv("D:\\history_A_stock_k_data.csv", index=False)
    # print(result)

    #### 登出系统 ####
    bs.logout()

    ohlc = result.rename(columns={'date': 'Date','open': 'O', 'high': 'H', 'low': 'L',
                                'close': 'C', #'Adj Close': 'AC',
                                'volume': 'V'})
    ohlc['Date'] = pd.to_datetime(ohlc['Date'])
    ohlc.set_index("Date", inplace=True)
    ohlc["O"] = ohlc["O"].astype("float")
    ohlc["H"] = ohlc["H"].astype("float")
    ohlc["L"] = ohlc["L"].astype("float")
    ohlc["C"] = ohlc["C"].astype("float")
    ohlc["V"] = ohlc["V"].astype("int")
    ohlc.info()
    # ohlc = ohlc.set_index('Date', drop=False)
    # ohlc = pybacktest.load_from_yahoo('GOOG')
    ohlc.tail()

    short_ma = 10
    long_ma = 20

    ms = ohlc.C.rolling(short_ma).mean()
    ml = ohlc.C.rolling(long_ma).mean()

    buy = cover = (ms > ml) & (ms.shift() < ml.shift())  # ma cross up
    sell = short = (ms < ml) & (ms.shift() > ml.shift())  # ma cross down

    print('>  Short MA\n%s\n' % ms.tail())
    print('>  Long MA\n%s\n' % ml.tail())
    print('>  Buy/Cover signals\n%s\n' % buy.tail())
    print('>  Short/Sell signals\n%s\n' % sell.tail())

    bt = pybacktest.Backtest(locals(), 'ma_cross')

    print(list(filter(lambda x: not x.startswith('_'), dir(bt))))
    print('\n>  bt.signals\n%s' % bt.signals.tail())
    print('\n>  bt.trades\n%s' % bt.trades.tail())
    print('\n>  bt.positions\n%s' % bt.positions.tail())
    print('\n>  bt.equity\n%s' % bt.equity.tail())
    print('\n>  bt.trade_price\n%s' % bt.trade_price.tail())

    bt.summary()


    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.rcParams['figure.figsize'] = (15.0, 8.0)

    bt.plot_equity()


    bt.plot_trades()
    ohlc.C.rolling(short_ma).mean().plot(c='green')
    ohlc.C.rolling(long_ma).mean().plot(c='blue')
    plt.legend(loc='upper left')

    # bt.trdplot['2018':'2020']
    # ohlc.C['2018':'2020'].rolling(short_ma).mean().plot(c='green')
    # ohlc.C['2018':'2020'].rolling(long_ma).mean().plot(c='blue')
    #
    plt.show()

    # pass
