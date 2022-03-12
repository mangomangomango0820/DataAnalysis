# _*_coding : UTF_8 _*_
# Author    : Xueshan Zhang
# Date      : 2022/3/12 3:48 PM
# File      : JiraReport_html.py
# Tool      : PyCharm

'''
1. connect with jira server, go to 2;
2.
2.1 search issue with filters (jql) and dump raw data;
2.2 clean raw data in 2.1, go to 3;
3. analyze data in 2.2 and format selected data in html, go to 4;
4. send email with html in 3, go to 5;
5. zip raw data in 2.1 for tracking in the future;

Reference:
1. https://python.hotexamples.com/examples/jira/JIRA/worklog/python-jira-worklog-method-examples.html
2. https://community.atlassian.com/t5/Jira-questions/worklog-timespent-by-user-by-issue-JQL/qaq-p/91233?tempId=eyJvaWRjX2NvbnNlbnRfbGFuZ3VhZ2VfdmVyc2lvbiI6IjIuMCIsIm9pZGNfY29uc2VudF9ncmFudGVkX2F0IjoxNjQ1NDMxODY5MTYzfQ%3D%3D#U1950537
3. https://jira.atlassian.com/browse/JRASERVER-34311
'''

import pandas as pd
import datetime, time, json, re
from collections import OrderedDict

import os, zipfile

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

from jira import JIRA, resources, Worklog

import logging
logging.basicConfig(
    level=logging.INFO,                                                                  # info level to be exported
    format='%(asctime)s: %(levelname)s  %(message)s',                                    # output msg format
    datefmt='%Y-%m-%d %A %H:%M:%S',                                                      # date format
    filename='./output log',                                                             # path to be exported the output log file
    filemode='w')                                                                        # mode of writing output file,
                                                                                         # w, rewrite; a, add;
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  # filename, .py itself
console.setFormatter(formatter)                                                          # format of console output msg
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)


def _SendEmail(info):
    message = MIMEMultipart('mixed')
    message['From'] = info['sender']
    message['To'] = info['receiver']
    message['CC'] = info['cc']
    message['Subject'] = Header(info['header'], 'utf-8').encode()

    link = "http://jira.local:8080/browse/TD-X"

    html = f"""\
       <html>
       <head>
       </head>
       <body>
              <basefont size="2" color="dark" face="Times New Roman, Arial">
              <p><b>{"Refer to"}<a href={link}> this link</a>{" for more information."}</b><br></p>
              <p><br></p>
              {info['content']}
              </basefont>
       </body>

       </html>
       """
    part1 = MIMEText(html, 'html')
    message.attach(part1)

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(info['server'], 25)
        smtpObj.sendmail(info['sender'], info['receiver'], message.as_string())
        logging.info("Success: Sent.")
    except smtplib.SMTPException as e:
        logging.info("Error: Unable to Send Email with ", str(e))
    else:
        smtpObj.quit()
        logging.info('Quit SMTP.')


if __name__ == '__main__':
    path = 'path'
    DebugFlag = True                                                                                # True, debug mode;
                                                                                                    # False, no

    ###### 1. connect with jira server, go to 2;
    try:
        server = JIRA(server=address, basic_auth=(username, password))
    except Exception as e:
        logging.info(f"{e}.")
    logging.info(str(datetime.datetime.now()) + ' > Connect Server Done.')


    ###### 2.
    ###### 2.1 search issue with filters (jql) and dump raw data;
    if not os.path.exists(path):
        os.makedirs(path)
    fields = ['worklog', 'reporter', 'status', 'summary', 'updated', 'id', 'key']

    ###### dump raw data in json [optional]
    ### tips: jql_str, e.g 'project = TD ORDER BY priority DESC, updated DESC'
    if DebugFlag:
        Issues = server.search_issues(jql_str=jql, maxResults=maxResults, json_result=True, expand='changelog', fields=fields)
        toStr = json.dumps(obj=Issues, ensure_ascii=False, indent=4, sort_keys=True, separators=(",", ": "))
        fn = path + '/raw.json'
        f = open(fn, 'w', encoding='utf-8')
        f.write(toStr)
        f.close()
        # with open(fn, 'w', encoding='utf-8') as f:
        #     f.write(toStr)
        #     f.close()

    RawData = []
    for each in server.search_issues(jql, maxResults=maxResults):
        # each 'TD-X'    ; type(each),     '<class 'jira.resources.Issue'>'
        # each.key 'TD-X'; type(each.key), '<class 'str'>'
        issue = server.issue(each.key, fields=fields)
        for worklog in issue.fields.worklog.worklogs:
            logDate = datetime.datetime.strptime(worklog.updated, "%Y-%m-%dT%H:%M:%S.%f+0800")
            today = datetime.datetime.today()
            if today - logDate <= datetime.timedelta(days=7):
                d = OrderedDict()
                d['logged'] = worklog.updated
                d['updated'] = issue.fields.updated
                d['reporter'] = worklog.updateAuthor.displayName
                d['summary'] = issue.fields.summary
                d['key'] = issue.key
                d['comment'] = worklog.comment
                d['status'] = issue.fields.status
                d['project'] = issue.fields.project
                d['priority'] = issue.fields.customfieldsxxx
                d['timeSpentHrs'] = worklog.timeSpentSeconds / 3600
                RawData.append(d)
    data = pd.DataFrame(RawData)
    if DebugFlag:
        with pd.ExcelWriter(path + '/raw.xlsx') as writer:
            RawData.to_excel(writer, sheet_name='raw')
            logging.info(str(datetime.datetime.now()) + ' > Export Raw Data.')
    logging.info(str(datetime.datetime.now()) + ' > Fetch Raw Data Done.')

    ##### 2.2 clean raw data in 2.1, go to 3;
    # RawData = pd.read_excel(path + '/raw.xlsx', sheet_name='raw').drop(['Unnamed: 0'], axis=1)
    data['reporter'] = data['reporter'].str.split(',', 1, expand=False).str[0]
    data['logged'] = pd.to_datetime(data['logged']).dt.tz_localize(None)
    data['updated'] = pd.to_datetime(data['updated']).dt.tz_localize(None)
    logging.info(str(datetime.datetime.now()) + ' > Clean Data Done.')


    ##### 3. analyze data in 2.2 and format selected data in html, go to 4;
    reporterVal = set(data['reporter'].to_list())
    priorityOrder = ['High', 'Medium', 'Low', 'Cancel', 'NA']
    prjOrder = set(data['project'].to_list())

    contentind = {}
    contentall = ''''''
    for pp in reporterVal:
        sum = ''''''
        sum += '<p>' + '<font size="3">' + '<b>' + pp + '</b>' + '</font>' + '<br/>' + '</p>'
        for priority in priorityOrder:
            for prj in prjOrder:
                idxList = data.loc[(data['priority'] == priority) & (data['updateAuthor'] == pp) & (data['project'] == prj)].index.to_list()
                if len(idxList) != 0:
                    sum += '<p>' + '<b>' + priority + '</b>' + '<br/>' + '</p>'
                    for idx in idxList:
                        prj = data.iloc[idx]['project']
                        summary = data.iloc[idx]['summary']
                        efforts = data.iloc[idx]['timeSpentHrs'].round(2)
                        comment = data.iloc[idx]['comment']
                        sum += '<ul>'
                        if type(comment) is str:                                                    # has comment
                            updated = data.iloc[idx]['updated']
                            today = datetime.datetime.today()
                            if updated - today >= datetime.timedelta(days=-2):
                                comment = '<font color="darkblue">' + data.iloc[idx]['comment'] + '</font>'
                            if comment.count('_x000D_') < 1:                                        # comment: 1 line
                                if sum.count(prj + summary) == 1:
                                    sum += ', ' + f"{comment}"
                                else:
                                    sum += '<li>' + f"{prj + summary}" + ", " + f"{comment}"
                            else:                                                                   # comment: >1 lines
                                pattern = r"_x000D_"
                                fmtcomment = re.sub(pattern, " ", comment)
                                if fmtcomment.count('#') >= 0:
                                    fmt = fmtcomment.replace('#', ';')
                                if sum.count(prj + summary) == 1:
                                    sum += ', ' + f"{fmt}"
                                else:
                                    sum += '<li>' + f"{prj + summary}" + ", " + f"{fmt}"
                            sum += '</li>'
                        else:                                                                       # no comment
                            if sum.count(prj + summary) == 0:
                                sum += '<li>' + f"{prj + summary}" + '<br/>' + '</li>'
                        sum += '</ul>'
        sum += '<p>' + '<br/>' + '</p>'
        contentind[pp.lower()] = sum
        contentall += sum


    ###### 4. send email with html in 3, go to 5;
    mailInfo = {
        'server': '10.216.116.116',
        'sender': 'sender@gmail.com',
        'receiver': None,
        'header': 'Week' + str(datetime.datetime.today().isocalendar()[1]),
        'content': None
    }

    receivers = [
        'receiverA@gmail.com',
        'receiverB@gmail.com',
        'receiverC@gmail.com',
        'VIP@gmail.com'
    ]

    for pp in contentind:
        for email in receivers:
            if pp == email.split(sep='@')[0].lower():
                receiver = email
                mailInfo['receiver'] = receiver
                if pp != 'vip':
                    mailInfo['content'] = contentind[pp]
                    _SendEmail(info=mailInfo)
                else:
                    mailInfo['content'] = contentall
                    _SendEmail(info=mailInfo)
    logging.info(str(datetime.datetime.now()) + ' > Mail Done.')


    ##### 5. zip raw data in 2.1 for tracking in the future;
    toPath = './' + path + '/' + path + '.zip'
    fromPath = path + '/RawData.xlsx'
    toFolder, toFilename = os.path.split(toPath)
    Export = zipfile.ZipFile(toPath, 'w')
    Export.write(fromPath)
    Export.close()
    logging.info(str(datetime.datetime.now()) + ' > Zip Done.')




