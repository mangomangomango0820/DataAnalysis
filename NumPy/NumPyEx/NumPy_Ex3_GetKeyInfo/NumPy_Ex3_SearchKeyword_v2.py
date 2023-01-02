# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2023/1/2 5:14 PM
# File      : NumPy_Ex3_SearchKeyword_v2.py
# Tool      : PyCharm


# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/12/22 3:52 PM
# File      : Numpy_FindKeyword.py
# Tool      : PyCharm

import os
import sys
import re
import logging
import numpy as np
import pandas as pd
import datetime

import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s: %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
    filename=f"{os.path.basename(__file__).split('.')[0]}.log",
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

def read_in_chunks(path, chunk_size = 5*1024):
    object = open(path)
    while True:
        chunk_data = object.read(chunk_size)
        if not chunk_data:
            break
        yield chunk_data

if __name__ == '__main__':

    # todo: Section 1.
    # directory path as input
    dir = 'YourDirectory'
    # target file extension to be analyzed, e.g '.log'
    extension = 'YourTargetExtension'
    # keywords to be found
    keywords = ['A', 'B', 'C']
    # define file name to be exported
    Export = f"KeyInfo_{datetime.date.today()}.xlsx"

    # if the 'dir' is a valid variable point to existing directory
    isDir = os.path.isdir(dir)
    if not isDir:
        sys.exit(f"Error: Check input variable '{dir}'.")
    else:
        logging.debug(f"Ready to analyze files in '{dir}'")

    # list all files in dir
    files = os.listdir(dir)
    files = np.array(files)
    # find the index of files that its extension ends with .log
    idx = np.char.endswith(a=files, suffix=extension)
    # get a list of files with target extension
    logs = files[idx]
    # get a list of file path of files with target extension
    logs = np.char.add(dir, logs)
    logging.debug(f"Files To be Analyzed:\n{logs}.")


    # todo: Section 2.
    OUTPUT = {}
    for log in logs:
        points = {}
        for chunk in read_in_chunks(log):
            lines = chunk.splitlines()
            lines = np.array(lines)
            for keyword in keywords:
                # find the index of keyword in lines
                keyword_idx = np.char.find(a=lines, sub=keyword)
                # find the line where includes the index
                line = lines[keyword_idx>-1]
                # if the number of lines is larger than 0
                if line.shape[0] > 0:
                    # find the last number in the matched line
                    value = re.findall(r'\d+\.?\d*', line[-1][-1])
                    points[keyword] = value
        OUTPUT[os.path.basename(log)] = points

    df = pd.DataFrame.from_dict(OUTPUT).T
    df = df.reset_index()
    df = df.rename(columns={'index': 'FILE'})

    df['file'] = df['FILE'].str.split('_').str[3] + df['FILE'].str.split('_').str[4]
    newcollabels = ['FILE', 'file'] + keywords
    df = df.reindex(newcollabels, axis=1)
    df.to_excel(Export, index=False, header=True)


    # todo: Section 2.
    OUTPUT = {}
    for log in logs:
        points = {}
        f = open(log, 'r', encoding='UTF-8')
        lines = f.readlines()
        for line in lines:
            for keyword in keywords:
                flag = re.search(keyword, line)
                if flag is not None:
                    value = re.findall(r"\d+\.?\d*", line)[-1]
                    points[keyword] = value
        OUTPUT[os.path.basename(log)] = points

    df = pd.DataFrame.from_dict(OUTPUT).T
    df = df.reset_index()
    df = df.rename(columns={'index': 'FILE'})
    df.to_excel(Export, index=False, header=True)


    # todo: Section 2.
    OUTPUT = {}
    for log in logs:
        points = {}
        f = open(log, 'r', encoding='UTF-8')
        lines = f.readlines()
        taillines = lines[-500:]
        lines = np.array(taillines)
        for keyword in keywords:
            linesFocus = np.char.find(a=lines, sub=keyword)
            linesFocus = lines[linesFocus>-1][-1]
            value = re.findall(r"\d+\.?\d*", line)[-1]
            points[keyword] = value
        OUTPUT[os.path.basename(log)] = points
        f.close()

    df = pd.DataFrame.from_dict(OUTPUT).T
    df = df.reset_index()
    df = df.rename(columns={'index': 'FILE'})
    df.to_excel(Export, index=False, header=True)


