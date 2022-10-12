# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/10/12 9:24 PM
# File      : NumPy_Ex2_DataProcess.py
# Tool      : PyCharm

import pandas as pd
import numpy as np

'''
1 pc connect with 16 devices (4 devices / pc) via 16-port usb hub, or 
16 COMS -> 4 devices/pc * 4 pcs

1. generate a coms np with shape (160, 1), COM_cnt * PC_cnt = 16 * 10;
2. generate a PCs np with shape (160, 1), PC_cnt * COM_cnt = 10 * 16;
3. generate a NVMEs np with shape (160, 1), NVME_cnt * ip_cnt = 4 * 40;
4. generate a ips np with shape (160, 1), ip_cnt * NVME_cnt = 40 * 4;
5. horizontally concat 4 nps, get shape (160, 4)
6. export final result as dataframe;
'''

COM_cnt = 16
PC_cnt = 10
NVME_cnt = 4
ip_cnt = 40


# 1. generate a coms np with shape (160, 1), COM_cnt * PC_cnt = 16 * 10;
np_COMs = np.array(['COM' + str(i) for i in range(3, 3+COM_cnt)]).reshape(COM_cnt, 1)
# [['COM3']
#  ['COM4']
#  ...
#  ['COM17']
#  ['COM18']]
#
# shape, (16, 1)
np_all_COMs = np.tile(np_COMs, reps=(PC_cnt, 1))
# shape, (160, 1)


# 2. generate a PCs np with shape (160, 1), PC_cnt * COM_cnt = 10 * 16;
PC_segment = '121.1.3.'
PC_postfix = [i for i in range(PC_cnt)]
np_PCs = np.array([PC_segment + str(i) for i in PC_postfix]).reshape(PC_cnt, 1)
# [['121.1.3.0']
#  ['121.1.3.1']
#  ...
#  ['121.1.3.8']
#  ['121.1.3.9']]
#
# shape, (10, 1)
np_all_PCs = np.repeat(np_PCs, repeats=COM_cnt).reshape(PC_cnt*COM_cnt, 1)
# shape, (160, 1)


# 3. generate a NVMEs np with shape (160, 1), NVME_cnt * ip_cnt = 4 * 40;
np_NVME = np.array(['NVME' + str(i) for i in range(NVME_cnt)]).reshape(1, NVME_cnt)
# [['NVME0' 'NVME1' 'NVME2' 'NVME3']]
#
# shape, (1, 4)
np_all_NVMEs = np.tile(np_NVME, reps=ip_cnt).reshape(ip_cnt*NVME_cnt, 1)
# shape, (160, 1)


# 4. generate a ips np with shape (160, 1), ip_cnt * NVME_cnt = 40 * 4;
ip_segment = '127.0.1.'
ip_postfix = [i for i in range(50, 50+ip_cnt)]
np_ip = np.array([ip_segment + str(i) for i in ip_postfix]).reshape(ip_cnt, 1)
# [['127.0.1.50']
#  ['127.0.1.51']
#  ...
#  ['127.0.1.88']
#  ['127.0.1.89']]
#
# shape, (40, 1)
np_all_ips = np.repeat(np_ip, repeats=NVME_cnt, axis=0)
# [['127.0.1.50']
#  ['127.0.1.50']
#  ['127.0.1.50']
#  ['127.0.1.50']
#  ...
#  ['127.0.1.89']
#  ['127.0.1.89']
#  ['127.0.1.89']
#  ['127.0.1.89']]
# shape, (160, 1)


# 5. horizontally concat 4 nps, get shape (160, 4)
result = np.hstack((np_all_ips, np_all_NVMEs, np_all_PCs, np_all_COMs))
#  ['127.0.1.50' 'NVME0' '121.1.3.0' 'COM3']
#  ['127.0.1.50' 'NVME1' '121.1.3.0' 'COM4']
#  ...
#  ['127.0.1.89' 'NVME2' '121.1.3.9' 'COM17']
#  ['127.0.1.89' 'NVME3' '121.1.3.9' 'COM18']]
#
# shape, (160, 4)


# 6. export final result as dataframe;
data = pd.DataFrame(result)
data.columns = ['IP', 'NVME', 'PC', 'COM']
data.to_excel('NumPy_Ex2_DataProcess.xlsx', header=None, index=False)