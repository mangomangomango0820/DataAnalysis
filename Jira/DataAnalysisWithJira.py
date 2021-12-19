#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Purpose:
# @Last Modified: 2021/11/1

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'
import pandas as pd
import datetime
from collections import OrderedDict
from pprint import pprint
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

import logging

logging.basicConfig(
    level=logging.INFO,  # level of info output to log file
    format='%(asctime)s: %(levelname)s  %(message)s',  # format of output msg
    datefmt='%Y-%m-%d %A %H:%M:%S',  # date format
    filename='output log',  # name of output log file
    filemode='w')  # mode of writing output file,
# w, rewrite; a, add;

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  # filename, .py itself
# format of console output msg
console.setFormatter(formatter)
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

from jira import JIRA


def _ConnectJiraServer(info):
    server = info['server']
    username = info['username']
    password = info['password']

    try:
        db = JIRA(server=server, basic_auth=(username, password))
    except Exception as e:
        raise RuntimeError(f"Exception: {e}.")

    return db


def _SearchIssues(con):
    db = con['db']
    jql = con['jql']
    maxResults = con['maxResults']

    issuesList = db.search_issues(jql, maxResults=maxResults)

    return issuesList


def _RawData(con):
    db = con['db']
    list = con['list']

    RawData = []
    for each in list:
        issue = db.issue(each.key, expand='changelog')

        for worklog in issue.fields.worklog.worklogs:
            d = OrderedDict()
            d['updateAuthor'] = worklog.updateAuthor.displayName
            d['emailAddress'] = worklog.updateAuthor.emailAddress
            d['timeSpent'] = worklog.timeSpent
            d['timeSpentHrs'] = worklog.timeSpentSeconds / 3600
            d['key'] = issue.key
            d['summary'] = issue.fields.summary

            if issue.fields.assignee:
                d['assignee'] = issue.fields.assignee.displayName
            else:
                d['assignee'] = issue.fields.assignee
            d['issueType'] = issue.fields.issuetype.name
            d['updated'] = worklog.updated
            RawData.append(d)
    RawDataDF = pd.DataFrame(RawData)

    return RawDataDF


def _CleanData(data):
    # pick up 1 series and save its copy
    # data['A'] -> data['A'].to_list() -> set(data['A'].to_list()))
    # series          -> list                      -> set
    MailReceivers = set(data['emailAddress'].to_list())
    print(MailReceivers)

    # split the string of 1 series at 1 dataframe, e.g. Coral Zhang
    # data['updateAuthor'].str.split(' ', 1, expand=False).str[0]
    # Coral Zhang -> Coral
    # data['updateAuthor'].str.split(' ', 1, expand=False).str[1]
    # Coral Zhang -> Zhang
    print(data['updateAuthor'].head())
    split = ('updateAuthor', 'assignee')
    for i in split:
        data[i] = data[i].str.split(' ', 1, expand=False).str[0]
    print(data['updateAuthor'].head())

    # filter data according to datetime
    # convert time
    # 2021-10-27T10:38:23.342+0800 (raw data) -> pd.to_datetime -> 2021-10-27 10:38:23.342000+08:00 (<class 'pandas._libs.tslibs.timestamps.Timestamp'>)
    # 2021-10-27 10:38:23.342000+08:00 -> dt.tz_localize(None) -> 2021-10-27 10:38:23.342
    # 2021-10-27 10:38:23.342 -> dt.strftime('%Y-%m-%d') -> 2021-10-27 (<class 'str'>)
    data['updated'] = pd.to_datetime(data['updated']).dt.tz_localize(None)
    # data['updated'] = pd.to_datetime(data['updated'], format="%Y-%d-%m, %H:%M:%S")
    # data['updated'] = pd.to_datetime(data['updated'], infer_datetime_format=True)

    today = pd.to_datetime('today').normalize()
    LastSevenDaysdata = data[data['updated'].between(today - pd.offsets.Day(7), today)]

    # drop specific columns
    dataMail = data.drop(['timeSpentHrs', 'emailAddress', 'updated', 'issueType'], axis=1)

    return data, LastSevenDaysdata


def _GroupData(con):  # data should be raw data
    data = con['db']
    attribute = con['attribute']
    target = con['target']

    groupdata = []
    for i in range(len(attribute)):
        g = data.groupby(attribute[i]).agg('sum')
        gd = g[target]
        groupdata.append(gd)

    return groupdata


def _ProcessData(con):  # data should be raw data, process data by week

    data = con['db']
    attribute = con['attribute']
    target = con['target']

    data.set_index(['updated'], drop=True, inplace=True)
    week = data.index.isocalendar().week
    updated = data.index
    MultiIndex = [week, updated]

    data = data.set_index(MultiIndex)
    week = data.index.names[0]
    updated = data.index.names[1]
    data.sort_index(axis=0, level=[0, 1], inplace=True)

    PV = []
    Per = []
    for i in range(len(attribute)):
        A = data.groupby([week, attribute[i]])[target].sum()
        A = pd.DataFrame(A)  # series -> dataframe, index ['week', 'issueType']
        logging.info(f"Group by {week} & {attribute[i]}, Sum {target}")

        B = data.groupby(week)[target].sum()
        B = pd.DataFrame(B)  # series -> dataframe, index 'week'
        logging.info(f"Group by {week}, Sum {target}")

        PIVOT = data.pivot_table(index='week',
                                 columns=attribute[i],
                                 values=target,
                                 aggfunc='sum',
                                 fill_value=0)
        logging.info(f'Transverse Table')
        PV.append(PIVOT)

        RESULT = pd.merge(PIVOT, B, left_on=['week'], right_index=True, how='outer')
        logging.info(f'Full Table: ')

        df_total = RESULT[RESULT.columns[-1]]
        df = RESULT[RESULT.columns[:-1]]
        df_rel = df.div(df_total, 0)
        logging.info(f'Final Table')
        Per.append(df_rel)

    return PV, Per


def _PiePlot(data, figsize=(5, 5), title=None, name=None):
    plot = data.plot.pie(figsize=figsize, autopct='%1.1f%%', title=title)
    p = plot.get_figure()
    p.savefig(name + '.png')
    plt.close()


def _StackedBarPlot(data, per, figsize=(8, 5), title=None, ylabel=None, name=None, size=6):
    #      x: week, y: hrs, mark: percentage
    p = data.plot.bar(rot=0, figsize=figsize, stacked=True, title=title)
    plt.ylabel(ylabel)

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
    for index, row in per.reset_index().iterrows():
        for item in per.columns:
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
                    p.text(loc[i]['x'], loc[i]['y'], text[i]['text'], horizontalalignment='center', size=size)
    except Exception as e:
        raise Exception
    else:
        plt.draw()
        plt.pause(3)
        plt.savefig(name + '.png')
        plt.close()


def _SendEmail(server, sender, receiver, cc, header=None, pic=None, link=None, data=None):
    message = MIMEMultipart('mixed')
    message['From'] = sender
    message['To'] = ";".join(receiver)
    message['CC'] = cc
    message['Subject'] = Header(header, 'utf-8').encode()

    imgid = []
    for i in pic:
        pic = MIMEBase(i, 'png')
        pic.add_header('Content-ID', i)
        imgid.append(i)
        with open(i + '.png', 'rb') as f:
            pic.set_payload(f.read())
        encoders.encode_base64(pic)
        message.attach(pic)

    # html
    html = f"""\
    <html>

    <head></head>

    <body>
        <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
            <table border="1" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td>
                        <h2 style="color:darkblue;"> X </h2>
                    </td>
                </tr>
                <tr>
                    <td>
                        <table border="1" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                                <td width="240" valign="top">
                                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td>
                                                <img src="cid:{imgid[0]}">
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 0px 0 0 0;">
                                                {''}
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                                <td style="font-size: 0; line-height: 0;" width="20">
                                    &nbsp;
                                </td>
                                <td width="240" valign="top">
                                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td>
                                                <img src="cid:{imgid[1]}">
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 0px 0 0 0;">
                                                {''}
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    <td>

                <tr>
                    <td>

                        <li>
                            <p><a href={link}>More Details :</a></p>
                        </li>
                        {pd.DataFrame(data).round(2).to_html(classes='table table-striped')}
                    </td>
                </tr>
            </table>
        </td>
    </body>

    </html>
    """
    part1 = MIMEText(html, 'html')
    message.attach(part1)

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(server, 25)
        smtpObj.sendmail(sender, receiver, message.as_string())
        logging.info("Success: Sent.")
    except smtplib.SMTPException as e:
        logging.info("Error: Unable to Send Email with ", str(e))
    else:
        smtpObj.quit()
        logging.info('Quit SMTP.')


if __name__ == '__main__':

    ###### 1. Connect with Jira
    JiraServer = {
        'server': 'Z',
        'username': 'X',
        'password': 'Y'
    }

    db = _ConnectJiraServer(info=JiraServer)
    logging.info('> Connect Jira Server.')

    ###### 2. Fetch Raw Data and Clean it
    SearchCondition = {
        'db': db,
        'jql': 'Filter',
        'maxResults': '-1'
    }

    issuesList = _SearchIssues(con=SearchCondition)

    FetchCondition = {
        'db': db,
        'list': issuesList
    }

    RawDataDF = _RawData(con=FetchCondition)

    logging.info('> Fetch Raw Data')

    data, LastSevenDaysdata = _CleanData(data=RawDataDF)
    logging.info('Clean Data Per Requirement')

    ###### 3. Group / Process Data
    GroupCondition = {
        'db': data,
        'attribute': ('updateAuthor', 'issueType'),
        'target': 'timeSpentHrs'
    }

    ### group
    groupdata = _GroupData(con=GroupCondition)
    logging.info('Group Data')

    ### process
    processdata, Per = _ProcessData(con=GroupCondition)
    logging.info('Process Data')

    ###### 4. Plot
    ###    pie plot
    PiePlt = {
        'title': ('NameA', 'NameB'),
        'name': ('NameC', 'NameD')
    }

    if len(PiePlt['title']) == len(groupdata):
        for i in range(len(groupdata)):
            _PiePlot(data=groupdata[i], title=PiePlt['title'][i], name=PiePlt['name'][i])
    logging.info('Pie Plots Done')

    ### stacked plotIn
    BarPlt = {
        'title': ('Name1', 'Name2'),
        'name': ('Name3', 'Name4')
    }

    if len(BarPlt['title']) == len(processdata):
        for i in range(len(processdata)):
            _StackedBarPlot(data=processdata[i], per=Per[i], title=BarPlt['title'][i], ylabel='Hours',
                            name=BarPlt['name'][i])
    logging.info('Stacked Plots Drawing Done')

    ###### Send Email
    memberList = [
        'A@gmail.COM',
        'B@gmail.COM',
    ]

    mailInfo = {
        'server': 'xxx',
        'sender': 'xG@gmail.com',
        'receiver': memberList,  # memberList
        'cc': 'A@gmail.com',
        'header': 'Week' + str(processdata[0].index[-1] + 1),
        'pic': (PiePlt['name'][0], BarPlt['name'][1]),
        'link': 'xxx',
        'data': groupdata[0]
    }

    _SendEmail(server=mailInfo['server'], sender=mailInfo['sender'], receiver=mailInfo['receiver'], cc=mailInfo['cc'],
               header=mailInfo['header'], pic=mailInfo['pic'], link=mailInfo['link'], data=mailInfo['data'])
    logging.info('Auto Send Email')