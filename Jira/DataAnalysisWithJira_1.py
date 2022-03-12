#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Purpose:
# @Last Modified: 2021/11/11
# @Author: Xueshan Zhang


from jira import JIRA
import pandas as pd
from collections import OrderedDict
import matplotlib.pyplot as plt
import logging

logging.basicConfig(
    level=logging.INFO,                                             # level of info output to log file
    format='%(asctime)s: %(levelname)s  %(message)s',               # format of output msg
    datefmt='%Y-%m-%d %A %H:%M:%S',                                 # date format
    filename='output log',                                          # name of output log file, e.g. output log
    filemode='w')                                                   # mode of writing output file,
                                                                    # w, rewrite; a, add;

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  # filename, .py itself
# format of console output msg
console.setFormatter(formatter)
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)


def _ConnectJiraServer(info):
    '''

    :param info: based on info, connect with jira server
    :return: db: database
    '''
    server = info['server']
    username = info['username']
    password = info['password']

    try:
        db = JIRA(server=server, basic_auth=(username, password))
    except Exception as e:
        raise RuntimeError(f"Exception: {e}.")

    return db


def _SearchIssues(con):
    '''

    :param con: based on given search condition 'con', dump raw data from jira
    :return: issueList
    '''
    db = con['db']
    jql = con['jql']
    maxResults = con['maxResults']

    issuesList = db.search_issues(jql, maxResults=maxResults)

    import json
    issueList_json = db.search_issues(jql, maxResults=-1, json_result=True, expand='changelog')
    issueListDump = json.dumps(obj=issueList_json, ensure_ascii=False, indent=4, sort_keys=True,
                               separators=(",", ": "))             # <class 'str'>

    fn = 'rawdata.json'                                            # fn: file name, e.g rawdata.json
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(issueListDump)
        f.close()

    return issuesList


def _RawData(con):
    '''

    :param con: based on given conditions, e.g. db (database) and list (issueList), dump raw data
    :return: RawDataDF
    '''
    db = con['db']
    list = con['list']

    RawData = []
    for each in list:
        changelog = db.issue(each.key, expand='changelog').changelog
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status' and item.toString == 'Done':
                    d = OrderedDict()
                    d['creator'] = each.fields.creator.displayName
                    ...
                    d['created'] = each.fields.created
                    d['summary'] = each.fields.summary
                    d['reporter'] = each.fields.customfield_10805
                    ...
                    d['priority'] = each.fields.priority
                    RawData.append(d)

    RawDataDF = pd.DataFrame(RawData)

    return RawDataDF


def _CleanData(data):
    '''

    :param data: based on given data, normalize data and do primary processing per requirement
    :return: data
    '''
    # normalize to DateTime dtype
    data['created'] = pd.to_datetime(data['created']).dt.tz_localize(None)

    # drop duplicates on subset 'creator'
    data.drop_duplicates(subset='creator', inplace=True, keep='last')

    return data


if __name__ == '__main__':

    ###### 1. Connect with Jira with given info, e.g. server address, userID and passwrd
    JiraServer = {
        'server': 'server address',
        'username': 'userID',
        'password': 'passwrd'
    }

    db = _ConnectJiraServer(info=JiraServer)
    logging.info('> Connect Jira Server.')


    ###### 2. Search on given conditions, e.g. get all jira under project 'XXX' without limitation on the number of
    # result
    SearchCondition = {
        'db': db,
        'jql': 'project = XXX',
        'maxResults': '-1'
    }
    issuesList = _SearchIssues(con=SearchCondition)
    logging.info('Search Issues')

    FetchCondition = {
        'db': db,
        'list': issuesList
    }
    RawDataDF = _RawData(con=FetchCondition)
    logging.info('Fetch Raw Data')

    data = _CleanData(data=RawDataDF)
    logging.info('Clean Data Per Requirement')

    # optional: export raw data as xlsx file, e.g. 'rawdata.xlsx'
    data.to_excel('rawdata.xlsx', index=True)
    # optional: import raw data from xlsx file, e.g. 'rawdata.xlsx', drop redundant column 'Unnamed: 0' and fill empty
    # cell with str 'None'
    data = pd.read_excel('rawdata.xlsx')
    data.reset_index()
    data = data.drop(labels='Unnamed: 0', axis=1).fillna('None')


    ###### 3. process raw data per requirement
    # group by 2 elements, 2 elements as tuple multi-index, export multi-index to a list
    tuple_creatorANDreporter = data.groupby(['creator', 'reporter']).agg('sum').index.to_list()
    '''
    [('AR', 'F'), ('BW', 'P'), ...]
    '''

    # give a mapping dict between old element 'creator' and new element 'group'
    dict_creator_to_group = {
        ('DJ', 'RH'): 'XY',
        ('LL', 'WY', 'XZ'): 'WY',
        ('BW', 'YJ'): 'BW',
    }

    # generate a mapping dict based on old elements 'creator' and 'reporter' to new element 'group'
    dict_creatorANDreporter_to_group= {}
    for i in tuple_creatorANDreporter:
        if i[1] != 'P' or i[1] == 'None':
            dict_creatorANDreporter_to_group[i] = 'Other'
        else:
            for j in dict_creator_to_group:
                if i[0] in j:
                    dict_creatorANDreporter_to_group[i] = dict_creator_to_group[j]
    '''
    {('AR', 'F'): 'Other', ('BW', 'P'): 'BW', ...}
    '''

    data['group'] = data[['creator', 'reporter']].apply(lambda x: dict_creatorANDreporter_to_group.get((x.creator, x.reporter)), axis=1)


    ###### 4. generate pivot table per requirement
    pivot = data.pivot_table(
        index='group',
        columns='priority',
        aggfunc='count',
        fill_value=0
    )


    ##### 5. plot a stacked bar plot and export it, e.g. 'stackedBarPlot.png
    plot = pivot.plot.bar(rot=0, stacked=True, figsize=(8, 5))
    plt.ylabel('y axis')
    plt.draw()
    plt.pause(3)
    plt.savefig('stackedBarPlot.png')
    plt.close()