# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/12/23 10:42 AM
# File      : NumPy_Ex3_SearchKeyword.py
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
from tkinter import ttk
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


def read_in_chunks(path, chunk_size=5 * 1024):
    object = open(path)
    while True:
        chunk_data = object.read(chunk_size)
        if not chunk_data:
            break
        yield chunk_data


class window:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Window")
        self.root.geometry("600x300+420+280")
        self.interface()

    def interface(self):
        labelDir = tk.Label(self.root, text='Directory')
        labelDir.grid(row=0, padx=10, pady=5)
        self.entryDir = tk.Entry(self.root, width=50)
        self.entryDir.grid(row=0, column=2, padx=10, pady=10)

        labelFiles = tk.Label(self.root, text='Files')
        labelFiles.grid(row=2, padx=10, pady=5)
        self.textFiles = tk.Text(self.root, width=65, height=5)
        self.textFiles.grid(row=2, column=2, padx=10, pady=10)

        labelExp = tk.Label(self.root, text='Export')
        labelExp.grid(row=3, padx=10, pady=5)
        self.entryExp = tk.Entry(self.root, width=50)
        self.entryExp.grid(row=3, column=2, padx=10, pady=10)

        btnOpen = tk.Button(self.root, text='Open', command=self.browse).place(relx=0.2, rely=0.85, relwidth=0.1, relheight=0.1)
        btnGen = tk.Button(self.root, text='Generate', command=self.generate).place(relx=0.45, rely=.85, relwidth=0.1, relheight=0.1)
        btnExit = tk.Button(self.root, text='Exit', command=self.root.quit).place(relx=0.7, rely=0.85, relwidth=0.1, relheight=0.1)

        self.prog = ttk.Progressbar(self.root, mode='indeterminate', length=100)
        self.prog.place(relx=0.35, rely=0.7, relwidth=0.3, relheight=0.05)
        self.prog.start()

    def browse(self):
        self.entryDir.delete(0, END)
        self.textFiles.delete('0.0', 'end')
        self.entryExp.delete(0, END)

        self.dir = filedialog.askdirectory(
            title='Open Directory'
        )
        self.entryDir.insert('insert', self.dir)


        # todo: Section 1.
        # if the 'dir' is a valid variable point to existing directory
        isDir = os.path.isdir(self.dir)
        if not isDir:
            sys.exit(f"Error: Check variable '{self.dir}'.")
        else:
            logging.debug(f"Ready to analyze files in '{self.dir}'")

        # list all files in dir
        files = os.listdir(self.dir)
        files = np.array(files)
        # find the index of files that its extension ends with .log
        idx = np.char.endswith(a=files, suffix=extension)
        # get a list of files with target extension
        logs = files[idx]
        selflog = f'{os.path.basename(__file__).split(".")[0]}.log'
        if selflog in logs:
            logs = np.delete(logs, np.where(logs == selflog))
            print(f"after delete: {logs}")
        else:
            print(f"do not have to delete")
        if logs.shape[0] == 0:
            messagebox.showerror(title='Error', message='Currently, no file extension matches with ".log".')
        else:
            for log in logs:
                self.textFiles.insert('end', log+'\n')
            self.logs = np.char.add(self.dir+'/', logs)
            logging.debug(f"Logs: {self.logs}.")

    def generate(self):
        dir = self.entryDir.get()
        dir = dir + '/'

        # todo: Section 2.
        OUTPUT = {}
        for log in self.logs:
            points = {}
            for keyword in keywords:
                logging.debug(f"\n")
                logging.debug(f"Keyword: {keyword}")
                values = []
                for chunk in read_in_chunks(log):
                    lines = chunk.splitlines()
                    lines = np.array(lines)
                    # find the index of keyword in lines
                    keyword_idx = np.char.find(a=lines, sub=keyword)
                    # find the line where includes the index
                    matches = lines[keyword_idx > -1]
                    # if the number of lines is larger than 0
                    if matches.shape[0] > 0:
                        for match in matches:
                            # find the hour:minute:second in the matched line
                            value = re.findall(r'\d{1,2}:\d{1,2}:\d{1,2}', match)
                            values.append(value)
                            logging.debug(f"Match: {match}")
                            logging.debug(f"Value: {value}")
                points[keyword] = values
            OUTPUT[os.path.basename(log)] = points
            df = pd.DataFrame.from_dict(OUTPUT).T
            df = df.reset_index()
            df = df.rename(columns={'index': 'FILE'})
            # df['file'] = df['FILE'].str.split('_').str[0] + df['FILE'].str.split('_').str[1]
            # newcollabels = ['FILE', 'file'] + keywords
            # df = df.reindex(newcollabels, axis=1)
            # define file name to be exported
            Export = f"{self.dir}/KeyInfo_{datetime.date.today()}.xlsx"
            df.to_excel(Export, index=False, header=True)
            self.entryExp.insert('insert', Export)
            break

        messagebox.showinfo(title='Done', message=f'Export to "{Export}".')
        self.prog.stop()


if __name__ == '__main__':

    # target file extension to be analyzed, e.g '.log'
    extension = '.log'
    # keywords to be found
    keywords = ['packet', 'interface', 'rc', 'stateMachine']

    win = window()
    win.root.mainloop()
