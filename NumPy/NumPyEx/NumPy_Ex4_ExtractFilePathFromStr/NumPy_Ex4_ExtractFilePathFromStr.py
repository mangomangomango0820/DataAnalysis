# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2023/5/15 00:03
# File      : NumPy_Ex4_ExtractFilePathFromStr.py
# Tool      : PyCharm

import os.path
import numpy
import re
import datetime
import numpy as np

### 1. global variables;
# relative file path to be parsed, e.g. 'NumPy_Ex4_Example.log' or '/User/xxx/.../NumPy_Ex4_Example.log';
FileToParse = 'NumPy_Ex4_Example.log'
# category to be parsed;
Category = ['america', 'china', 'germany', 'Egypt']
# the date of the day to run this script in format '%Y%m%d';
TodayDate = datetime.date.today().strftime("%Y%m%d")
# relative file path to save parsed content;
FileToOutput = f'NumPy_Ex4_ParsedFile_{TodayDate}'

### 2. filter targets;
# re sentence;
# here in this case, re sentence should be 'america{1}\/.*|china{1}\/.*|germany{1}\/.*|egypt{1}\/.*';
filter = ""
if Category.__len__() == 1:
    filter = f"{Category[0]}{1}\/.*"
else:
    for ca in Category:
        filter += f"{ca}" + "{1}\/.*"
        if ca != Category[-1]:
            filter += "|"
        else:
            break
# add results to 'output' list;
output = []
f = open(FileToParse, "r")
for line in f:
    result = re.findall(filter, line)
    if result.__len__() == 1:
        output.append(result[0])
    else:
        continue
f.close()
# convert output list to output numpy array, and save processed array as 'FileToOutput';
output = np.array(output)
output = np.unique(output)
output.sort(axis=0, kind='mergesort')
output = np.flipud(output)
print(output,'\n',output.shape)
np.savetxt(FileToOutput, output, fmt="%s")