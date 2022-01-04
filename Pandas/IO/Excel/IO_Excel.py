# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/1/4 7:59 PM
# File      : Excel.py
# Tool      : PyCharm

import pandas as pd
import os
import zipfile


# 1. find or create a directory named 'Dir' in desired path
folder = "/Users/xueshanzhang/PycharmProjects/pythonProject1214/DataAnalysis/Pandas/IO/Excel/Dir"
if not os.path.exists(folder):
    os.makedirs(folder)


# 2. read from excel in target path 'Pandas/RawData.xlsx'
# /RawData.xlsx' as Dataframe
data = pd.read_excel(io='/Users/xueshanzhang/PycharmProjects/pythonProject1214/DataAnalysis/Pandas/RawData.xlsx')
# ```
# print(data.head(5))
#
#           id        uid  ... diqu  city
# 0  553217640  6376967.0  ...   广西   南宁市
# 1  553217639  6376967.0  ...   广西   南宁市
# 2  553217638  6571870.0  ...  浙江省   杭州市
# 3  553217637  7215034.0  ...  陕西省   NaN
# 4  553217636  7190777.0  ...  云南省   昆明市
#
# [5 rows x 11 columns]
# ```


# 3. write Dataframe into excel per requirement and save it in desired path
# 3.1 write 1 sheet to 1 xlsx named '1sheet.xlsx'
data.to_excel(folder+'/1Sheet.xlsx',
              sheet_name='Sheet-1',
              float_format='%.2f',
              na_rep='Empty',
              index=False)

# 3.2 write multiple sheets to 1 xlsx, e.g. here write ```data``` into 2 sheets and 2 sheets in the same xlsx file
# '2Sheets.xlsx'
with pd.ExcelWriter(
        folder+'/2Sheets.xlsx',
        datetime_format='YYYY-MM-DD') as writer:
    data.to_excel(writer, sheet_name='Sheet-1')
    data.to_excel(writer, sheet_name='Sheet-2')


# 4. pack files
# 4.1 ZipFile
# 4.1.1 single file
# generate a zip file named 'output.zip' in desired path 'folder' and save as a variable 'OutputZip';
# write target file '1Sheet.xlsx' in target path into 'OutputZip' and close it
OutputZip = zipfile.ZipFile(folder+'/output.zip', 'w')
OutputZip.write(folder+'/1Sheet.xlsx')
OutputZip.close()

# 4.1.2 multiple fils in same dir
# generate a zip file named 'output.zip' in desired path 'folder' and save as a variable 'OutputZip';
# change working directory to target path, and write target files in current wd into 'OutputZip' and close it
with zipfile.ZipFile(folder+'/Output.zip', 'w') as OutputZip:
    os.chdir(folder)
    OutputZip.write('1Sheet.xlsx')
    OutputZip.write('2Sheets.xlsx')
    OutputZip.close()