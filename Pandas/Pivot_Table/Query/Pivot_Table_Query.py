# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2021/12/19 1:20 PM
# File      : Pivot_Table_Query.py
# Tool      : PyCharm


import pandas as pd
import npm


'''
'''

names = ['user', 'uid', 'title', 'docid', 'time', 'status', 'score', 'qudao', 'kffs', 'province', 'city']
data = pd.read_excel(io='/Users/xueshanzhang/PycharmProjects/pythonProject1214/DataAnalysis/Pandas/RawData.xlsx', names=names)
'''
print(data.columns)
Index(['user', 'uid', 'title', 'docid', 'time', 'status', 'score', 'qudao',
       'kffs', 'province', 'city'],
      dtype='object')
'''

pivot = data.pivot_table(
    index=['province', 'uid'],
    columns='kffs',
    values=['docid', 'score'],
    aggfunc={'docid': 'count', 'score': 'sum'},
    fill_value=0,
    margins=True,
    margins_name='SumAll',
    observed=True,
    sort=True
)
'''
print(pivot)
                   docid             score             
kffs                   1   2 SumAll      1     2 SumAll
province        uid                                           
云南省      125825.0    1   0    NaN    0.0   0.0    NaN
...                  ...  ..    ...    ...   ...    ...
黑龙江省   7213955.0    2   0    1.0    1.1   0.0    1.1
...                  ...  ..    ...    ...   ...    ...
SumAll               225  41  266.0  269.0  52.5  321.5

[279 rows x 6 columns]


print(pivot.index)
MultiIndex([(   '云南省',  125825.0),
            ...
            (  '黑龙江省', 7185586.0),
            ...
            ('SumAll',        '')],
           names=['province', 'uid'], length=279)


print(pivot.columns)
MultiIndex([('docid',        1),
            ...
            ('docid', 'SumAll'),
            ('score',        1),
            ...
            ('score', 'SumAll')],
           names=[None, 'kffs'])
'''