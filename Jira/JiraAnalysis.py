# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/1/10 8:23 PM
# File      : JiraAnalysis.py
# Tool      : PyCharm

'''
1. Connect with Jira server;
2. fetch faw data;
3. process data;
4. plot: pie plot & stacked bar plot;
5. zip
'''

import time, datetime, os, json, shutil
from jira import JIRA
import matplotlib.pyplot as plt

import pandas as pd
from collections import OrderedDict

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
    filename='logging.log',
    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)


if __name__ == '__main__':

    ### target path to store all generated files in the steps below
    path = './Data'
    if not os.path.exists(path):
        os.makedirs(path)

    ###### 1. connect with jira server
    try:
        server = JIRA(server=address, basic_auth=(username, password))
    except Exception as e:
        logging.info(f"{e}.")
    logging.info(str(datetime.datetime.now())+' Connect with Jira server.')


    ###### 2.
    ###### 2.1 dump raw data in json [optional]
    ### tips: jql_str, e.g 'project = TD ORDER BY priority DESC, updated DESC'
    Issues = server.search_issues(jql_str=jql, maxResults=maxResults, json_result=True, expand='changelog')
    DumpIssues = json.dumps(obj=Issues, ensure_ascii=False, indent=4, sort_keys=True, separators=(",", ": "))
    with open(path+'/RawData.json', 'w', encoding='utf-8') as f:
        f.write(DumpIssues)
        f.close()

    ###### 2.2 fetch raw data in dataframe
    RawData = []
    for each in server.search_issues(jql_str=jql, maxResults=maxResults):
        issue = server.issue(each.key, expand='changelog')
        for worklog in issue.fields.worklog.worklogs:
            d = OrderedDict()
            d['people'] = worklog.updateAuthor.displayName
            d['type'] = issue.fields.issuetype.name
            d['status'] = issue.fields.status
            d['key'] = issue.key
            d['logged'] = worklog.updated
            d['TotalHrs'] = issue.fields.timespent / 3600
            ######
            # based on json file, add data to ```d```
            ######
            RawData.append(d)
    data = pd.DataFrame(RawData)
    logging.info(str(datetime.datetime.now()) + ' Fetch Raw data.')

    ###### 2.3 formatting per requirement
    ### tips: data['A'] -> data['A'].to_list()
    #         series    -> list
    ### tips: data['B'].str.split(',', 1, expand=False).str[0]
    #         Coral, Zhang -> Coral + Zhang
    data['people'] = data['people'].str.split(',', 1, expand=False).str[0]
    ### tips: 2021-10-27T10:38:23.342+0800     -> pd.to_datetime          -> 2021-10-27 10:38:23.342000+08:00
    #         2021-10-27 10:38:23.342000+08:00 -> dt.tz_localize(None)    -> 2021-10-27 10:38:23.342
    #         2021-10-27 10:38:23.342          -> dt.strftime('%Y-%m-%d') -> 2021-10-27
    data['logged'] = pd.to_datetime(data['logged']).dt.tz_localize(None)
    # data['updated'] = pd.to_datetime(data['updated'], format="%Y-%d-%m, %H:%M:%S")
    # data['updated'] = pd.to_datetime(data['updated'], infer_datetime_format=True)
    ### tips: today = pd.to_datetime('today').normalize()
    #         lastWeek = data[data['updated'].between(today - pd.offsets.Day(6), today)]
    logging.info(str(datetime.datetime.now()) + ' > Format data.')

    ###### 2.4 export raw data as xlsx [optional]
    with pd.ExcelWriter(path+'/RawData.xlsx') as writer:
        data.to_excel(writer, sheet_name='RawData')
        logging.info(str(datetime.datetime.now()) + ' > Export Raw Data in xlsx.')


    ###### 3. 
    ###### 3.1 import raw data from RawData.xlsx
    data = pd.read_excel(path+'/RawData.xlsx', sheet_name='RawData').drop(['Unnamed: 0'], axis=1)

    ###### 3.2 process data by Groupby and pivot_table methods
    ###### 3.2.1 multi-index: set time and week as multi-index
    ### tips: week = data.index.isocalendar().week
    data.set_index(['logged'], drop=True, inplace=True)
    week = data.index.isocalendar().week

    logged = data.index
    MultiIndex = [week, logged]
    data = data.set_index(MultiIndex)
    week = data.index.names[0]
    logged = data.index.names[1]
    ### tips: sort data according to multi-index level 0 and 1: data.sort_index(axis=0, level=[0, 1], inplace=True)
    data.sort_index(axis=0, level=1, inplace=True)

    ###### 3.2.2 group: group by 'week' and 'logged', and sum by 'TotalHrs'
    GroupA = data.groupby([week, 'people'], sort=False)['TotalHrs'].sum()
    GroupA = pd.DataFrame(GroupA)
    lastweek = GroupA.loc[(GroupA.index[-1][0], ), 'TotalHrs']

    GroupB = data.groupby(level=0, sort=False)['TotalHrs'].sum()

    ##### 3.2.3 pivot table: index by 'logged' and 'week', and sum by 'TotalHrs'
    PIVOT = data.pivot_table(index=['logged', 'week'],
                             columns='people',
                             values='TotalHrs',
                             aggfunc='sum',
                             fill_value=0,
                             observed=False)
    ### tips: drop index level 0 and reserve level 1 'week'
    PIVOT = PIVOT.droplevel(level=0)
    PIVOT = PIVOT.groupby('week', sort=False).sum()

    ##### 3.2.4 merge 'GroupB' and 'PIVOT' by index 'week'
    RESULT = pd.merge(PIVOT, GroupB, left_on=['week'], right_index=True, how='outer')

    df_total = RESULT[RESULT.columns[-1]]
    df = RESULT[RESULT.columns[:-1]]
    df_rel = df.div(df_total, 0)
    logging.info(str(datetime.datetime.now()) + ' > Process data per requirement.')


    ###### 4. Plot
    ###### 4.1 Pie Plot
    ### tips: pie plot for 'lastweek'
    prefix = 'Week'+str(PIVOT.index[-1])
    plot = lastweek.plot.pie(figsize=(5, 5), autopct='%1.1f%%', title=prefix+'_people')
    p = plot.get_figure()
    p.savefig(path+'/'+prefix+'Pie_WeekANDPeople.png')
    plt.close()
    logging.info(str(datetime.datetime.now()) + ' > Plot pie plot for last week data.')

    ###### 4.2 Stacked Bar Plot
    ### tips: stacked bar plot for full data
    p = PIVOT.plot.bar(rot=0, figsize=(8, 5), stacked=True, title=prefix+'_people')
    plt.ylabel(ylabel='Hrs')

    loc = []
    for index, row in data.reset_index().iterrows():
        height = 0
        val = 0
        for item in data.columns:
            if row[item] != 0:
                val += height / 2 + row[item] / 2
                height = row[item]
                d = OrderedDict()
                d['x'] = index
                d['y'] = val
                loc.append(d)

    text = []
    for index, row in df_rel.reset_index().iterrows():
        for item in df_rel.columns:
            if row[item] != 0:
                vals = str(round(row[item] * 100, 1)) + '%'
                d = OrderedDict()
                d['x'] = index
                d['text'] = vals
                text.append(d)

    try:
        if len(loc) == len(text):
            for i in range(len(loc)):
                if loc[i]['x'] == text[i]['x']:
                    p.text(loc[i]['x'], loc[i]['y'], text[i]['text'], horizontalalignment='center', size=6)
    except Exception as e:
        raise Exception
    else:
        plt.draw()
        plt.pause(3)
        plt.savefig(path+'/'+prefix+'StackedBarPlot_WeekANDPeople.png')
        plt.close()
    logging.info(str(datetime.datetime.now()) + ' > Stacked Bar Plot for Full Data.')


    ###### 5. zip
    date = str(time.strftime('%Y-%m-%d',time.localtime(time.time())))
    toPath = './'+date+'output'
    shutil.make_archive(base_name=toPath, format='zip', root_dir=path)
    logging.info(str(datetime.datetime.now()) + ' > Pack folder into zip file.')