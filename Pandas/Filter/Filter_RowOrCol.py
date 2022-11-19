# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/11/19 2:27 PM
# File      : Filter_RowOrCol.py
# Tool      : PyCharm

import pandas as pd
import numpy as np

data = pd.read_excel(io='Filter_RawData.xlsx')
'''
print(data)
      Year     Sex  Rank  ...  None  Unnamed: 7 Unnamed: 8
0     1960  Female     1  ...   NaN         NaN        NaN
1     1960  Female     2  ...  Test         NaN        NaN
2     1960  Female     3  ...   NaN         NaN        NaN
3     1960  Female     4  ...   NaN         NaN        NaN
4     1960  Female     5  ...   NaN        Test        NaN
...    ...     ...   ...  ...   ...         ...        ...
3098  2021    Male    21  ...   NaN         NaN        NaN
3099  2021    Male    22  ...   NaN         NaN        NaN
3100  2021    Male    23  ...   NaN         NaN        NaN
3101  2021    Male    24  ...   NaN         NaN        NaN
3102  2021    Male    25  ...   NaN         NaN        NaN

[3103 rows x 9 columns]


print(data.columns)
Index(['Year', 'Sex', 'Rank', 'Name', 'Count', 'Data_Revision_Date', 'None',
       'Unnamed: 7', 'Unnamed: 8'],
      dtype='object')
      

print(data.index)
RangeIndex(start=0, stop=3103, step=1)
'''

# 1. filter columns
# 1.1 e.g select columns with label starting with 'Unnamed'
# @1
col_Unamed = data.filter(items=data.columns[list(data.columns.str.contains('Unnamed'))])
'''
print(col_Unnamed)
     Unnamed: 7 Unnamed: 8
0           NaN        NaN
1           NaN        NaN
2           NaN        NaN
3           NaN        NaN
4          Test        NaN
...         ...        ...
3098        NaN        NaN
3099        NaN        NaN
3100        NaN        NaN
3101        NaN        NaN
3102        NaN        NaN

[3103 rows x 2 columns]
'''


# @2
col_Unamed = data.filter(regex='Unnamed')
'''
print(col_Unnamed)
     Unnamed: 7 Unnamed: 8
0           NaN        NaN
1           NaN        NaN
2           NaN        NaN
3           NaN        NaN
4          Test        NaN
...         ...        ...
3098        NaN        NaN
3099        NaN        NaN
3100        NaN        NaN
3101        NaN        NaN
3102        NaN        NaN

[3103 rows x 2 columns]
'''


# @3
col_Unnamed = data.filter(like='Unnamed', axis=1)
'''
print(col_Unnamed)
     Unnamed: 7 Unnamed: 8
0           NaN        NaN
1           NaN        NaN
2           NaN        NaN
3           NaN        NaN
4          Test        NaN
...         ...        ...
3098        NaN        NaN
3099        NaN        NaN
3100        NaN        NaN
3101        NaN        NaN
3102        NaN        NaN

[3103 rows x 2 columns]
'''


# 1.2 e.g select columns with label ending with 'e'
# @1
col_e = data.filter(items=data.columns[list(data.columns.str.endswith('e'))])
'''
print(col_e)
         Name Data_Revision_Date  None
0       SUSAN         11/07/2022   NaN
1        MARY         11/07/2022  Test
2       KAREN         11/07/2022   NaN
3     CYNTHIA         11/07/2022   NaN
4        LISA         11/07/2022   NaN
...       ...                ...   ...
3098  MICHAEL         11/07/2022   NaN
3099   JAYDEN         11/07/2022   NaN
3100      LEO         11/07/2022   NaN
3101    DAVID         11/07/2022   NaN
3102   ADRIAN         11/07/2022   NaN

[3103 rows x 3 columns]
'''

# @2
col_e = data.filter(regex='e$', axis=1)
'''
print(col_e)
         Name Data_Revision_Date  None
0       SUSAN         11/07/2022   NaN
1        MARY         11/07/2022  Test
2       KAREN         11/07/2022   NaN
3     CYNTHIA         11/07/2022   NaN
4        LISA         11/07/2022   NaN
...       ...                ...   ...
3098  MICHAEL         11/07/2022   NaN
3099   JAYDEN         11/07/2022   NaN
3100      LEO         11/07/2022   NaN
3101    DAVID         11/07/2022   NaN
3102   ADRIAN         11/07/2022   NaN

[3103 rows x 3 columns]
'''



# 2. filter rows
# 2.1 e.g select rows with label '1962'
# @1
row_1962 = data.filter(like='1962', axis=0)
'''
print(row_1962)
      Year     Sex  Rank    Name  ...  Data_Revision_Date None Unnamed: 7 Unnamed: 8
1962  1999  Female    12  HANNAH  ...          11/07/2022  NaN        NaN        NaN

[1 rows x 9 columns]
'''

