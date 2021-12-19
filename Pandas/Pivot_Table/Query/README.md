<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Data Analysis](#data-analysis)
  - [Read file](#read-file)
  - [Info](#info)
  - [Pivot_Table](#pivot_table)
    - [Format](#format)
    - [Application](#application)
    - [Select](#select)
      - [Columns](#columns)
        - [*1.*](#1)
        - [*2.*](#2)
          - [*Label*](#label)
      - [Rows](#rows)
        - [*1.*](#1-1)
        - [*2.*](#2-1)
          - [*loc*](#loc)
          - [*iloc*](#iloc)
      - [columns & rows](#columns--rows)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<hr style=" border:solid; width:100px; height:1px;" color=#000000 size=1">
<br>



# Data Analysis
<font color=#999AAA >Make data analysis with a local file, e.g excel, with pandas, numpy, matplotlib and etc.
<br>




## Read file
*1.* 
read excel <br>
```data = pandas.read_excel(io='filename.xlsx')``` <br>
// read_excel, read_csv, read_json, …… <br>
```data = pd.read_excel(io='filename.xlsx', names=[A, B, C, ...])``` <br>
// read file content as data and rename its columns with list 'names'
<br>

## Info
*1.*
column <br>
```data.columns``` <br>
// type '<class 'pandas.core.indexes.base.Index'>', column names 

*2.*
index <br>
```data.index``` <br>
// type '', index names, type, item
<br>

## Pivot_Table
### Format
```angular2html
pivot_table(
    self,
    values=None,
    index=None,
    columns=None,
    aggfunc="mean",
    fill_value=None,
    margins=False,
    dropna=True,
    margins_name="All",
    observed=False,
    sort=True,
    )
```

### Application
in this case, apply to 'RawData.xlsx':
```angular2html
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
```
the result shows as:
```
                   docid             score             
kffs                   1   2 SumAll      1     2 SumAll
province        uid                                           
云南省      125825.0    1   0    NaN    0.0   0.0    NaN
...                  ...  ..    ...    ...   ...    ...
黑龙江省   7213955.0    2   0    1.0    1.1   0.0    1.1
...                  ...  ..    ...    ...   ...    ...
SumAll               225  41  266.0  269.0  52.5  321.5

[279 rows x 6 columns]
```
<br>

### Select
#### Columns
##### *1.*
- [x] ```pivot.columns``` <br>
// level 0 'None', level 1 'kffs'
```angular2html
MultiIndex([('docid',        1),
            ('docid',        2),
            ('docid', 'SumAll'),
            ('score',        1),
            ('score',        2),
            ('score', 'SumAll')],
           names=[None, 'kffs'])
```

##### *2.* 
###### *Label*
_All_
- [x] ```pivot[('score', )]``` _or_, ```pivot['score']``` <br>
// select all columns with MultiIndex ('score', ), or, level 0 index 'score'
```angular2html
kffs                    1     2  SumAll
province        uid                           
云南省      125825.0   0.0   0.0     NaN
...                   ...   ...     ...
黑龙江省    7213955.0  1.1   0.0     1.1
...                   ...   ...     ...
SumAll              269.0  52.5   321.5

[279 rows x 3 columns]
```

- [x] ```pivot[('score', )].columns```
```angular2html
Index([1, 2, 'SumAll'], dtype='object', name='kffs')
```

_1_
- [x] ```pivot[('score', 2)]```, _or_, ```pivot['score'][2]``` <br>
// select 1 column with MultiIndex ('score', 2), or, with level 0 index 'score' first and then level1 index 2
```angular2html
province         uid      
云南省       125825.0      0.0
                          ... 
黑龙江省     7213955.0     0.0
                          ...
SumAll                   52.5
Name: (score, 2), Length: 279, dtype: float64
```

_1< <All_ <br>
- [x] ```pivot[('score',)][[1,'SumAll']]```, _or_, ```pivot['score'][[1,'SumAll']]``` <br>
// select level 0 index 'score' first and then level1 index '1' & 'SumAll'
```angular2html
kffs                    1  SumAll
province uid                     
云南省    125825.0     0.0     NaN
...                   ...     ...
黑龙江省  7213955.0    1.1     1.1
...                   ...     ...
SumAll              269.0   321.5

[279 rows x 2 columns]
```
<br>

#### Rows
##### *1.*
- [x] ```pivot.index``` <br>
// level 0 'province', level 1 'uid'
```angular2html
MultiIndex([(   '云南省',  125825.0),
            ...
            (  '黑龙江省', 7185586.0),
            ...
            ('SumAll',        '')],
           names=['province', 'uid'], length=279)
```

##### *2.* 
###### *loc*
_All_
- [x] ```pivot.loc['云南省']``` <br>
// select all rows with level 0 index '云南省'
```angular2html
          docid           score            
kffs          1  2 SumAll     1    2 SumAll
uid                                        
125825.0      1  0    NaN   0.0  0.0    NaN
...
7213895.0     8  0    2.0   2.2  0.0    2.2
```

- [x] ```pivot.loc['云南省'].index```
```angular2html
Index([ 125825.0, 6331762.0, 6724869.0, 7088853.0, 7119058.0, 7119448.0,
       7166576.0, 7190777.0, 7208339.0, 7213895.0],
      dtype='object', name='uid')
```

_1_ <br>
- [x] ```pivot.loc[[('云南省', 7213895.0)]]``` <br>
// select 1 row with level 0 index '云南省' first and then level1 index '7213895.0'
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
云南省    7213895.0     8  0    2.0   2.2  0.0    2.2
```

_1< <All_
- [x] ```pivot.loc['云南省'].loc[[125825.0, 7213895.0]]``` <br>
// select not all but more than 1 row with level 0 index '云南省' <br>
// select level 0 index '云南省' first and then level1 index '125825.0' & '7213895.0' <br>
```angular2html
          docid           score            
kffs          1  2 SumAll     1    2 SumAll
uid                                        
125825.0      1  0    NaN   0.0  0.0    NaN
7213895.0     8  0    2.0   2.2  0.0    2.2
```
<br>

###### *iloc*
_All_ 
- [x] pivot.iloc[:-1] <br>
// select all rows 
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
云南省    125825.0      1  0    NaN   0.0  0.0    NaN
...                  ... ..    ...   ...  ...    ...
黑龙江省  7213860.0     6  0    1.0   1.5  0.0    1.5

[278 rows x 6 columns]
```

_1_
- [x] pivot.iloc[-2] <br>
// select Nr.-2 row
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
黑龙江省  7216985.0     4  0    1.0   1.8  0.0    1.8
```

_1< <All_
- [x] ```pivot.iloc[[1,4,13]]``` <br>
// select discrete rows per requirement, e.g. Nr.1th, 4th, 13th
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
云南省    6331762.0     4  0    1.0   1.4  0.0    1.4
         7119058.0     2  0    1.0   1.5  0.0    1.5
四川省    6181664.0     2  0    1.0   1.5  0.0    1.5
```

- [x] ```pivot.iloc[::150]``` <br>
// select discrete rows per fixed value, e.g. Nr.0, 150th
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
云南省    125825.0      1  0    NaN   0.0  0.0    NaN
湖南省    6971814.0     2  0    1.0   1.0  0.0    1.0
```

- [x] ```pivot.iloc[-5,-2]``` <br>
// select sequential rows in limited range
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
黑龙江省  7213955.0     2  0    1.0   1.1  0.0    1.1
         7216948.0     4  0    1.0   1.5  0.0    1.5
         7216960.0     6  0    2.0   2.0  0.0    2.0
```
<br>

###### *isin*
_1< <All_
- [x] ```pivot[pivot.index.get_level_values(level=0).isin(['湖北省', '湖南省'])]``` <br>
// select rows with level 0 index in list ['湖北省'， '湖南省']
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
湖北省    7099896.0     3  0    1.0   1.1  0.0    1.1
...
         7216989.0     4  0    1.0   1.5  0.0    1.5
湖南省    6226377.0     2  0    1.0   1.0  0.0    1.0
...
         7211310.0     2  0    NaN   0.0  0.0    NaN
```
<br>

###### *query*
_All_
- [x] ```pivot.query('province == "湖北省"')``` <br>
// select all rows with level 0 index '湖北省'
```angular2html
                   docid           score            
kffs                   1  2 SumAll     1    2 SumAll
province uid                                        
湖北省    7099896.0     3  0    1.0   1.1  0.0    1.1
         7178220.0     2  0    1.0   1.1  0.0    1.1
         7216989.0     4  0    1.0   1.5  0.0    1.5
```
<br>


#### Columns & Rows
###### *loc*
_Single Index_
- [x] ```pivot['docid'].loc[['黑龙江省']]``` <br>
// select column level 0 index 'docid' and row level 0 index '黑龙江省'
```angular2html
kffs                1  2  SumAll
province uid                    
黑龙江省  6981849.0  2  0     NaN
...
         7216985.0  4  0     1.0
```

_Multi Index_
- [x] ```pivot[('docid', 'SumAll')].loc[('黑龙江省', 7216985.0)]```, _or_,
<br> ```pivot[('docid', 'SumAll')][('黑龙江省', 7216985.0)]```       
// select column MultiIndex ('docid', 'SumAll') and row MultiIndex ('黑龙江省', 7216985.0) 
```angular2html
1.0
```
<br>