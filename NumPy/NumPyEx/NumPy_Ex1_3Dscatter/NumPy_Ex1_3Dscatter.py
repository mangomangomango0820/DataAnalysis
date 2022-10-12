# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/3/6 3:02 PM
# File      : NumPy_Ex1_3Dscatter.py
# Tool      : PyCharm

'''
purpose: 1. clean and process dataset, get data in the format of [x, y, z, ID]
         2. draw scatter plot:
            2.1 based on [7, y, z, ID] in dataset from 1.
            2.2 based on full dataset from 1.

Reference:
https://stackoverflow.com/questions/71359492/extract-an-ndarray-from-a-np-void-array/71360637#71360637
'''

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# 1. data analysis
# 1.1 load data from .npy file
DATA = np.load('NumPy_Ex1_3Dscatter_ExampleData.npy')
'''
[([   2,    2, 1920,  480],) ([   1,    3, 1923,  480],)
 ......
 ([   4,    1, 1920,  480],) ([   3,    0, 1922,  480],)
 ......
 ([   3,    3, 1923,  480],)]

⬆️ DATA.shape, (69,); DATA.dtype, [('f0', '<i8', (4,))]; type(DATA), <class 'numpy.ndarray'>

DATA[0], ([   2,    2, 1920,  480],)
⬆️ type(DATA[0]), <class 'numpy.void'>
'''

# 1.2 from numpy.void data to numpy.ndarray, seeing each row, e.g. [   2    2 1920  480], as [x, y, z, ID]
data = np.array(DATA.tolist()).squeeze(axis=1)
'''
DATA.tolist()
[(array([   2,    2, 1920,  480]),), ..., (array([   3,    3, 1923,  480]),)]
⬆️ type(DATA.tolist()), <class 'list'>

np.array(DATA.tolist())
[[[   2    2 1920  480]]

 [[   1    3 1923  480]]
 ....

 [[   3    3 1923  480]]]
⬆️ np.array(DATA.tolist()).shape, (69, 1, 4); np.array(DATA.tolist()).dtype, int64; type(np.array(DATA.tolist())), <class 'numpy.ndarray'>;

np.array(DATA.tolist()).squeeze(axis=1)
[[   2    2 1920  480]
 [   1    3 1923  480]
 ......
 [   3    3 1923  480]]
⬆️ np.array(DATA.tolist()).squeeze(axis=1).shape, (69, 4); np.array(DATA.tolist()).squeeze(axis=1).dtype, int64;
type(np.array(DATA.tolist()).squeeze(axis=1))，<class 'numpy.ndarray'>
'''

# 1.3 get unique valus in nr.0 row
allx = np.unique(data[:, 0])                                                            # a set of unique x values
'''
[0 1 2 3 4 5 6 7]
⬆️ np.unique(data[:, 0]).shape, (8,)
'''


# 2. scatter plot
# 2.1 starting with, e.g. x=7, in dataset got from 1.
fig = plt.figure(figsize=(6, 6))
ax = plt.axes(projection='3d')
                                                                                        # [7, y, z, ID]
i = 7
xi = data[np.where(data[:, 0] == i)]
xix, xiy, xiz = np.hsplit(xi[:, 0:3], 3)
ax.scatter3D(xix, xiy, xiz, s=40, c=xiz, marker='o', alpha=0.8, edgecolor='white')
                                                                                        # ticks
tickls, tickc = 5, 'black'
xmin, xmax = data[:, 0].min(), data[:, 0].max()
ymin, ymax = data[:, 1].min(), data[:, 1].max()
zmin, zmax = data[:, 2].min(), data[:, 2].max()
ax.set_xlim(xmin=xmin-1, xmax=xmax+1)
ax.set_xticklabels(range(xmin-1, xmax+1, 1), color=tickc)
ax.tick_params(axis='x', labelsize=tickls)
ax.set_ylim(bottom=ymin - 1, top=ymax + 1)
ax.set_yticklabels(range(ymin - 1, ymax + 1, 1), color=tickc)
ax.tick_params(axis='y', labelsize=tickls)
ax.set_zlim(bottom=zmin - 1, top=zmax + 1)
ax.set_zticklabels(range(zmin - 1, zmax + 1, 1), color=tickc)
ax.tick_params(axis='z', labelsize=tickls)
                                                                                        # test
for idx in range(xi.shape[0]):
    ax.text(x=xix[idx][0], y=xiy[idx][0], z=xiz[idx][0], s=xi[idx][1:3], zdir='x', fontsize=5)
                                                                                        # labels
labelfd = {'size': 8, 'color': 'black'}
ax.set_xlabel('X', fontdict=labelfd)
ax.set_ylabel('Y', fontdict=labelfd)
ax.set_zlabel('Z', fontdict=labelfd)
                                                                                        # title
ax.set_title(f"x={i}", loc='left', fontsize=8)
plt.suptitle("Single(x=7)", x=0.5, y=0.92, fontsize=16, color='red')
plt.savefig("NumPy_Ex1_3Dscatter_Single(x=7).png", dpi=300)

# 2.2 based on the dataset got from 1.
fig = plt.figure(figsize=(12, 12))
for i in allx:
    ax = fig.add_subplot(2, 4, i+1, projection='3d')                                    # create subplot
    xi = data[np.where(data[:, 0] == i)]
    xix, xiy, xiz = np.hsplit(xi[:, 0:3], 3)                                            # [0~7, y, z, ID]
    ax.scatter3D(xix, xiy, xiz, s=40, c=xiz, marker='o')
                                                                                        # ticks
    tickls, tickc = 5, 'black'
    xmin, xmax = data[:, 0].min(), data[:, 0].max()
    ymin, ymax = data[:, 1].min(), data[:, 1].max()
    zmin, zmax = data[:, 2].min(), data[:, 2].max()
    ax.set_xlim(xmin=xmin - 1, xmax=xmax + 1)
    ax.set_xticklabels(range(xmin - 1, xmax + 1, 1), color=tickc)
    ax.tick_params(axis='x', labelsize=tickls)
    ax.set_ylim(bottom=ymin - 1, top=ymax + 1)
    ax.set_yticklabels(range(ymin - 1, ymax + 1, 1), color=tickc)
    ax.tick_params(axis='y', labelsize=tickls)
    ax.set_zlim(bottom=zmin - 1, top=zmax + 1)
    ax.set_zticklabels(range(zmin - 1, zmax + 1, 1), color=tickc)
    ax.tick_params(axis='z', labelsize=tickls)
                                                                                       # annotation
    for idx in range(xi.shape[0]):
        ax.text(x=xix[idx][0], y=xiy[idx][0], z=xiz[idx][0], s=xi[idx][1:3], zdir='x', fontsize=3)
                                                                                       # labels
    labelfd = {'size': 8, 'color': 'black'}
    ax.set_xlabel('X', fontdict=labelfd)
    ax.set_ylabel('Y', fontdict=labelfd)
    ax.set_zlabel('Z', fontdict=labelfd)
                                                                                       # title
    ax.set_title(f"x={i}", loc='right', fontsize=8)
    plt.suptitle("Full(x=[0,8])", x=0.5, y=0.88, fontsize=16, color='red')
plt.savefig("NumPy_Ex1_3Dscatter_Full(x=[0,8]).png", dpi=300)