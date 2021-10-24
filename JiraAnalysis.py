# !/usr/bin/env python3
'''
author: Xueshan Zhang
date  : 2021/10/24 data analysis with Jira software
'''


from jira import *
from collections import OrderedDict
from pprint import pprint
from IPython.core.interactiveshell import InteractiveShell
from tkinter import *
import pandas as pd
import datetime
import random
InteractiveShell.ast_node_interactivity = 'all'


# 1. connect with jira
# Connect: connect with jira: server address, basic authentication info (username, password);
server = 'xxx'
username = 'xxx'
password = 'xxx'

try:
    JiraSum = JIRA(server=server, basic_auth=(username, password))
except:
    raise RuntimeError("Error.")
else:
    print('> Connect.')





# 2. dump raw data and do data analysis
# 2.1 check the list of all projects with user access;
print('> Full Project List (With User Access): ')
AllProj = JiraSum.projects()                   # <class 'list'>
AllProjList = []
for i in range(len(AllProj)):
    d = OrderedDict()
    d['Project'] = AllProj[i]
    AllProjList.append(d)
AllProjDF = pd.DataFrame(AllProjList)          # <class 'pandas.core.frame.DataFrame'>


# 2.2 manipulate specified project, e.g. xxx
print('> Target Project:')
TargetProj = JiraSum.project('xxx')            # <class 'jira.resources.Project'>
TargetProjInfo = []
d = OrderedDict()
d['Project'] = TargetProj.key
d['Name'] = TargetProj.name
d['Lead'] = TargetProj.lead
TargetProjInfo.append(d)
TargetProjDF = pd.DataFrame(TargetProjInfo)    # <class 'pandas.core.frame.DataFrame'>


# 2.3 search issues with user-defined filters jql
jql = 'xxx'
issueList = JiraSum.search_issues(jql, maxResults=-1)
# <class 'jira.client.ResultList'>
# maxResults = -1, no limitation on issue number and return full search results


# # 2.4 option: dump issue list info and write to json file
# import json
# issueList_json = JiraSum.search_issues(jql, maxResults=-1, json_result=True) # <class 'dict'>
# issueListDump = json.dumps(obj=issueList_json, ensure_ascii=False, indent=4, sort_keys=True, separators=(",", ": ")) # <class 'str'>
#
# file = 'Jira_RawData.json'
# with open(file, 'w', encoding='utf-8') as f:
#     f.write(issueListDump)
#     f.close()                                  # f: <class '_io.BufferedReader'>
# with open(file,'rb') as f:
#     fc = json.load(f)                          # fc: file content, <class 'dict'>
#     # pprint(fc)
#     f.close()


# 2.5 collect raw data of issues being filtered
print('> Raw Data Table:')
issuesDict = []
for item in issueList:
    issue = JiraSum.issue(item.key, expand='changelog')                          # <class 'jira.resources.Issue'>
    for worklog in issue.fields.worklog.worklogs:
        d = OrderedDict()
        d['key'] = issue.key
        d['id'] = issue.id
        d['issueType'] = issue.fields.issuetype.name
        d['updateAuthor'] = worklog.updateAuthor.emailAddress
        d['timeSpent'] = worklog.timeSpent
        d['timeSpentHrs'] = worklog.timeSpentSeconds / 3600
        d['summary'] = issue.fields.summary
        if issue.fields.assignee:
            d['assignee'] = issue.fields.assignee.displayName
        else:
            d['assignee'] = issue.fields.assignee
        d['updated'] = worklog.updated
        issuesDict.append(d)
issueDF = pd.DataFrame(issuesDict)                                              # <class 'pandas.core.frame.DataFrame'>


# 2.6 formalize
# 2.6.1 assignee
print('  > Formalize Assignee')
issueDF['assignee'] = issueDF['assignee'].str.split(' ', 1, expand=False).str[0]
print(issueDF.head())

# 2.6.2 formalize assignee
print('  > Formalize Assignee')
issueDF['assignee'] = issueDF['assignee'].str.split(' ', 1, expand=False).str[0]


# 2.6.3 formalize 'updated' (timestamp) and set as index
print('  > Formalize Timestamp and Set as Index')
issueDF['updated'] = pd.to_datetime(issueDF['updated']).dt.tz_localize(None)    # timestamp: year/month/day/time, DateTime
                                                                                # <class 'pandas.core.series.Series'>
issueDF.set_index(['updated'], inplace=True)

# multi index
issueDF = issueDF.set_index([issueDF.index.isocalendar().week, issueDF.index])  # <class 'pandas.core.indexes.multi.MultiIndex'>
issueDF.sort_index(inplace=True)


# # or
# today = pd.to_datetime('today').normalize()
# issueDF['updated'] = pd.to_datetime(issueDF['updated']).dt.tz_localize(None).dt.strftime('%Y-%m-%d') # date: year/month/day, str
#                                                                                                      # <class 'pandas.core.series.Series'>
# issueDF.set_index(['updated'], inplace=True)                                   # set 'updated' (timestamp) as index
# print(type(issueDF.index))                                                     # <class 'pandas.core.indexes.base.Index'>


# 2.7 group
# 2.7.1 group by week and then issue type
resultA = issueDF.groupby(['week', 'issueType'])['timeSpentHrs'].sum()
resultA.to_csv('Report_By_Week.csv', index=True, header=True, encoding="utf-8")

# 2.7.2 group by issue type and resample by week
resultB = issueDF.groupby('issueType').resample('W', level=1)['timeSpentHrs'].agg('sum') # <class 'pandas.core.series.Series'>
Windex = resultB.index.get_level_values('updated').isocalendar().week  # <class 'pandas.core.series.Series'>
# reset index
resultDF = resultB.reset_index()                                       # <class 'pandas.core.frame.DataFrame'>
                                                                       # <class 'pandas.core.indexes.range.RangeIndex'>
WindexDF = Windex.reset_index()                                        # <class 'pandas.core.frame.DataFrame'>
                                                                       # <class 'pandas.core.indexes.range.RangeIndex'>
# concat 2 DF in axis 1
final = pd.concat([resultDF, WindexDF], axis=1)                        # <class 'pandas.core.frame.DataFrame'>
                                                                       # <class 'pandas.core.frame.DataFrame'>
# remove duplicate rows
final = final.drop_duplicates().T.drop_duplicates().T                  # <class 'pandas.core.frame.DataFrame'>
                                                                       # <class 'pandas.core.indexes.numeric.Int64Index'>
final.to_csv('Report_By_IssueType.csv', index=True, header=True, encoding="utf-8")

# # or
# result = issueDF.groupby(week).apply(
#     lambda sub: sub['updateAuthor'][sub['timeSpentHrs'].idxmax()]                   # <class 'pandas.core.series.Series'>
# )

# 2.7.3 group by last week
resultC = issueDF[issueDF['updated'].between(today-pd.offsets.Day(7), today)]

# 2.7.4 group by author
# group=issueDF.groupby('updateAuthor')[['timeSpent']].agg((['sum', 'mean']))(group)
resultD = issueDF.groupby('updateAuthor').agg('sum')

# 2.7.5 group by issue type
resultE = issueDF.groupby('issueType').agg('sum')





# 3. plot
import matplotlib.pyplot as plt
from itertools import groupby

# 3.1 stacked plot
# set week as index, column 'issueType', value 'timeSpentHrs', function 'sum'
result = resultA.pivot_table(index=['week'], columns=['issueType'], values='timeSpentHrs', aggfunc='sum')
result.to_csv('result.csv')
pic = result.plot.bar(figsize=(5, 5), stacked=True, title='Resource By Week')
fig = pic.get_figure()
fig.savefig("Resource_By_Week.png")


# 3.2 pie plot
fig = resultE['timeSpentHrs'].plot.pie(figsize=(5, 5), autopct='%1.1f%%', title='Resource Last Week')
plt.show()
plt.close()





# 4. send email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

mail_host = 'xxx'                                            # server address
mail_user = "xxx"                                    	     # mail address
mail_pass = "xxx"                                            # mail account password

sender = 'A@X.com'
receivers = ['A@X.com']                                  	 # receivers = ['123@gmail.com','abc@gmail.com']


# 4.1 generate mail content, MIME objects subtypes including plain, html and etc.
# 4.1.1 plain text-only email
message = MIMEText('Test.', 'plain', 'utf-8')
message['From'] = sender
message['To'] = ";".join(receivers)
message['Subject'] = Header('Title', 'utf-8')

try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)
    # smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("Sent.")
except smtplib.SMTPException as e:
    print("Error.", str(e))
else:
    smtpObj.quit()
    print('Quit.')

# 4.1.2 plain text with pic as attachment
message = MIMEMultipart('related')
message['From'] = sender
message['To'] = ";".join(receivers)
message['Subject'] = Header('Title', 'utf-8').encode()
#
# include pic
with open(r'xxx.png', 'rb') as f:
    pic = MIMEImage(f.read())
    pic.add_header('Content-ID','pic')
    message.attach(pic)
    # f.close()
#
# include text
text = '''
Test.
'''
msg = MIMEText(text, 'plain', 'utf-8')
message.attach(msg)
#
##### 1.
# smtp = smtplib.SMTP_SSL('smtp.xxxx.com')                                          # xxxx, server domain name
# smtp.login('username','password')                                                 # username, your mail address;
                                                                                    # password, email account password
##### 2.
try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)                                                  # 25: SMTP Port
    # smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("Sent.")
except smtplib.SMTPException as e:
    print("Error.", str(e))
else:
    smtpObj.quit()
    print('Quit.')

# 4.1.3 html
message = MIMEMultipart('mixed')                                                      # 采用related定义内嵌资源的邮件体
message['From'] = sender
message['To'] = ";".join(receivers)
message['Subject'] = Header('Title', 'utf-8').encode()

link='xxx'
with open(r'xxx.PNG','rb') as f:
    pic = MIMEImage(f.read())
    pic.add_header('Content-ID', 'xxx')
    message.attach(pic)
    f.close()
msghtml = f"""\
<html>
    <head></head>
    <body>
        <h3 style="color:darkblue;">Head</h3>
        <ul>
        <li>Test</li>
        </ul>
        <img src="cid:xxx">
        <ul>
        <li><p><a href=link> xxx </a></p></li>
        </ul>
    </body>
</html>
"""
mailcontent = MIMEText(msghtml, 'html')
message.attach(mailcontent)
try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)                                                  # 25: SMTP Port
    # smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("Sent.")
except smtplib.SMTPException as e:
    print("Error.", str(e))
else:
    smtpObj.quit()
    print('Quit.')


# 4.2 set timer to execute script
import os, time
key = 1
while key < 2:
    now_time = time.strftime("%H_%M")
    time.sleep(50)
    if now_time == "12_00":
        os.chdir(r"xxx")                                          # working direction of target py file for execution
        time.sleep(1)
        os.system('xxx.py')                                       # target py file
        print(now_time)
    else:
        print('Waiting')