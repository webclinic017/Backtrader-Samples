import tushare as ts
# 120分基础积分每分钟内最多调取500次，每次5000条数据，相当于23年历史
ts.set_token('bfd3e9a3465c7bce5bc2d6ddc82559023079451d6dc7890a058c3fdb') 

pro = ts.pro_api()



#直接保存，保存结果最近的bar在首行
df = ts.pro_bar(ts_code='600000.SH', adj='qfq', start_date='20000101', end_date='20200710')
df.to_csv('d:/1/600000qfq.csv')
