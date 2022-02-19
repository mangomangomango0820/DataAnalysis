# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/2/19 10:30 AM
# File      : NumPy_Ex0_rm_rows_between_2_array.py
# Tool      : PyCharm

'''
purpose: 1. 2 arrays with same dimension in axis 1 but not in axis 0;
         2. get XOR remove rows in array 1 if in array 2;
         3. optional:
            3.1 get all/randomly selected rows;
            3.2 get all elements;

Reference:
https://stackoverflow.com/questions/70789782/filter-rows-in-numpy-array-based-on-second-array
https://numpy.org/doc/stable/reference/generated/numpy.isin.html
'''

import numpy as np


####################################################
# 1. 2 arrays with same dimension in axis 1 but not in axis 0;
#########################################
# 1.1 get A (32, 1), B (32, 1), C (32, 1), D (32, 1);
###############################
# 1.1.1 get A
arrA = np.array(np.arange(8)).reshape(8, 1)
'''
np.array(np.arange(8)))
# [0 1 2 3 4 5 6 7]

np.array(np.arange(8)).reshape(8, 1)
# [[0]
#  [1]
# ......
#  [6]
#  [7]]
'''
###############################
A = np.repeat(a=arrA, repeats=4, axis=0)
'''
A
# [[0]
#  [0]
#  [0]
#  [0]
# ......
#  [7]
#  [7]
#  [7]
#  [7]]

A.shape
# (32, 1)
'''
###############################
# 1.1.2 get B
arrB = np.array(np.arange(4)).reshape(4, 1)
'''
np.array(np.arange(4))
# [0 1 2 3]

np.array(np.arange(8)).reshape(8, 1)
# [[0]
#  [1]
#  [2]
#  [3]]
'''
B = np.tile(A=arrB, reps=(8, 1))
'''
B
# [[0]
#  [1]
#  [2]
#  [3]
#  ......
#  [0]
#  [1]
#  [2]
#  [3]]

B.shape
# (32, 1)
'''
###############################
# 1.1.3 get C
D = 370
arrC = np.array([[i+D*4] for i in range(4)])
C = np.tile(A=arrC, reps=(8, 1))
'''
np.array([[i+D*4] for i in range(4)])
# [[1480]
#  [1481]
#  [1482]
#  [1483]]

C
# [[1480]
#  [1481]
#  [1482]
#  [1483]
#  ......
#  [1480]
#  [1481]
#  [1482]
#  [1483]]

C.shape
# (32, 1)
'''
###############################
# 1.1.4 get D
arrD = np.array(D)
D = np.tile(A=arrD, reps=(8*4, 1))
'''
np.array(D)
# 370

D
# [[370]
# ......
#  [370]]

D.shape
# (32, 1)
'''
###############################
# 1.2 get X (A+B+C+D) (32, 4);
X = np.hstack((A, B, C, D))
###############################
# 1.3 get Y (2, 4);
Y = np.array([[3, 0, 1480, 370], [3, 2, 1482, 370]])


####################################################
# 2. get XOR remove rows in array 1 if in array 2;
#########################################
# 2.1 process
# 2.1.1 process X
Xv = np.ascontiguousarray(X).view(np.dtype([('', X.dtype, X.shape[1])])).ravel()
'''
np.ascontiguousarray(X)
# [[   0    0 1480  370]
#  [   0    1 1481  370]
# ......
#  [   7    2 1482  370]
#  [   7    3 1483  370]]
# ⬆️ shape (32, 4)

np.ascontiguousarray(X).view(np.dtype([('', X.dtype, X.shape[1])]))
# [[([   0,    0, 1480,  370],)]
#  [([   0,    1, 1481,  370],)]
# ......
#  [([   7,    2, 1482,  370],)]
#  [([   7,    3, 1483,  370],)]]
# ⬆️ shape (32, 1)

np.ascontiguousarray(X).view(np.dtype([('', X.dtype, X.shape[1])])).ravel()
# [([   0,    0, 1480,  370],) ([   0,    1, 1481,  370],)
#  ([   0,    2, 1482,  370],) ([   0,    3, 1483,  370],)
# ......
#  ([   7,    0, 1480,  370],) ([   7,    1, 1481,  370],)
#  ([   7,    2, 1482,  370],) ([   7,    3, 1483,  370],)]
# ⬆️ shape (32, )
'''
###############################
# 2.1.2 process Y
Yv = np.ascontiguousarray(Y).view(Xv.dtype).ravel()
'''
np.ascontiguousarray(Y)
# [[   3    0 1480  370]
#  [   3    2 1482  370]]
# ⬆️ shape (2, 4)

np.ascontiguousarray(Y).view(Xv.dtype)
# [[([   3,    0, 1480,  370],)]
#  [([   3,    2, 1482,  370],)]]
# ⬆️ shape (2, 1)

np.ascontiguousarray(Y).view(Xv.dtype).ravel()
# [([   3,    0, 1480,  370],) ([   3,    2, 1482,  370],)]
# ⬆️ shape (2,)
'''
#########################################
# 2.2 isin
Z = X[np.isin(Xv, Yv, invert=True)]
'''
X[np.isin(Xv, Yv, invert=True)]
# [[   0    0 1480  370]
#  ......
#  [   2    3 1483  370]
#  [   3    1 1481  370]
#  [   3    3 1483  370]
#  ......
#  [   7    3 1483  370]]
# ⬆️ shape (30, 4)
'''


####################################################
# 3. optional:
rowCnt = Z.shape[0]
columnCnt = Z.shape[1]
#########################################
# 3.1 get all/randomly selected rows
###############################
# 3.1.1 get all rows;
for rowNr in range(rowCnt):
    print(Z[rowNr])
'''
[   0    0 1480  370]
# ⬆️ shape (4,)
......
[   7    3 1483  370]
# ⬆️ shape (4,)
'''
###############################
# 3.1.2 get randomly selected rows;
import random
rowNr = random.randint(0, rowCnt)
print(rowNr, Z[rowNr])
'''
Nr. 27 in Z
# [   7    1 1481  370]
# ⬆️ shape (4,)
'''
#########################################
# 3.2 get all elements;
###############################
# 3.2.1 ravel
for idx in range(rowCnt*columnCnt):
    print(Z.ravel()[idx])
###############################
# 3.2.2 for
for rowidx in range(rowCnt):
    for colidx in range(columnCnt):
        print(Z[rowidx][colidx])