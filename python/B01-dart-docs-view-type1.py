# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import httplib
import urllib
import time
import sqlite3
import sys


def get_post(url, uri, params):
    url_params = urllib.urlencode(params)
    url_header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko"}
    print("http://" + url + uri + "?" + url_params)
    conn = httplib.HTTPConnection(url)
    conn.request("POST", uri, url_params, url_header)
    response = conn.getresponse()
    result_data = response.read()
    conn.close()
    time.sleep(1)
    return result_data

rcp_no = str(sys.argv[1])

url = "dart.fss.or.kr"
uri = "/dsaf001/main.do"
params = {
    'rcpNo': rcp_no
}
base_html = BeautifulSoup(get_post(url, uri, params), "html.parser")
#print(base_html)

head_tag = base_html.head.find_all('script', type="text/javascript")
list_tiles = []
for head in head_tag:
    if 'initPage' in head.text:
        source_menu_text = head.text.split('function initPage')[1].split('currentDocValues')[0]
        for source_text in source_menu_text.split('new Tree.TreeNode({'):
            if 'function() {viewDoc(' in source_text:
                source_for_json = source_text.split(';}')[0] \
                    .replace('listeners: {', '') \
                    .replace('function() {viewDoc(', '[') \
                    .replace(')', '') \
                    .replace('\t', '') \
                    .replace('\r', '') \
                    .replace('\n', '') \
                    .replace("'", '') \
                    .replace('text: "', '') \
                    .replace('click: [', '|') \
                    .replace('",id:', '|')
                menus = source_for_json.split('|')
                list_tiles.append({
                    'menu_title': menus[0]
                    , 'menu_params': menus[2]
                })

data_extracted = []
for menu in list_tiles:
    # 1. 회사의 개요
    # 4. 주식의 총수 등
    # 4. 재무제표
    print(menu['menu_title'])
    menu_parameters = menu['menu_params'].split(', ')
    # ?rcpNo=",r_rcpNo,"&dcmNo=",r_dcmNo,"&eleId=",r_eleId,"&offset=",r_offset,"&length=",r_length,"&dtd=",r_dtd)
    url = "dart.fss.or.kr"
    uri = "/report/viewer.do"
    params = {
        'rcpNo': menu_parameters[0]
        , 'dcmNo': menu_parameters[1]
        , 'eleId': menu_parameters[2]
        , 'offset': menu_parameters[3]
        , 'length': menu_parameters[4]
        , 'dtd': menu_parameters[5]
    }
    # each_page = BeautifulSoup(get_post(url, uri, params), "html.parser")
    # print(each_page)

    credit_info = []
    stocks_info = []
    if 'I' in menu['menu_title'] and u'개요' in menu['menu_title']:
        print(menu['menu_title'])
        each_page = BeautifulSoup(get_post(url, uri, params), "html.parser")

        tags = each_page.find('body').findChildren()
        html_section = []
        html_string = ""
        for tag in tags:
            if 'section-2' in str(tag) or 'line-height:1.6em' in str(tag):
                html_section.append(html_string)
                html_string = ""
            html_string += str(tag)

        for section in html_section:
            if '신용평가' in str(section):
                credit = BeautifulSoup(section, "html.parser")
                credit_th_list = credit.find_all('th')
                credit_col_count = len(credit_th_list)
                if credit_col_count > 0:
                    credit_td_list = credit.find_all('td')
                    for credit_td in credit_td_list:
                        credit_info.append(credit_td.text)

            if 'Ⅰ. 발행할 주식의 총수' in str(section):
                stocks = BeautifulSoup(section, "html.parser")
                stocks_td_list = stocks.find_all('td')
                flag_extract = False
                for stocks_td in stocks_td_list:
                    if 'Ⅰ. 발행할 주식의 총수' in str(stocks_td):
                        if not flag_extract:
                            flag_extract = True
                        else:
                            break
                    if flag_extract:
                        stocks_info.append(stocks_td.text)

    len_credit = len(credit_info) / 5
    for index in range(len_credit):

        evaluate_date = credit_info[index * 5][1:len(credit_info[index * 5])].replace("'", "").replace(".", "")
        if evaluate_date[0:1] == '9':
            evaluate_date = "19" + evaluate_date
        else:
            evaluate_date = "20" + evaluate_date

        data_extracted.append({
            'rcp_number': menu_parameters[0]
            , 'section': 'credit'
            , 'category': evaluate_date
            , 'values':credit_info[index * 5 + 2]
            , 'comment': '(' + credit_info[index * 5 + 1] + ')-(' + credit_info[index * 5 + 4] + ')-(' + credit_info[index * 5 + 3] + ')'
        })

    # stocks_info
    len_stocks = len(stocks_info) / 5
    for index in range(len_stocks):
        data_extracted.append({
            'rcp_number': menu_parameters[0]
            , 'section': 'preferred-stocks'
            , 'category': stocks_info[index * 5]
            , 'values': stocks_info[index * 5 + 2]
            , 'comment': '(' + credit_info[index * 5 + 4] + ')'
        })
        data_extracted.append({
            'rcp_number': menu_parameters[0]
            , 'section': 'stocks'
            , 'category': stocks_info[index * 5]
            , 'values': stocks_info[index * 5 + 1]
            , 'comment': '(' + credit_info[index * 5 + 4] + ')'
        })

    if 'I' in menu['menu_title'] and u'재무' in menu['menu_title']:
        print(menu['menu_title'])
        #print(each_page)

conn = sqlite3.connect('dart.sqlite')
curr = conn.cursor()
try:
    curr.execute("""
    create table dart_summary_imsi (
        rcp_number     bigint
        , section      text
        , category     text
        , datas        text
        , comments     text
    )
    """)
    conn.commit()
except:
    curr.execute(""" delete from dart_summary_imsi """)
    conn.commit()

loop_count = 0
for row in data_extracted:
    loop_count += 1
    SQL = ("""
    insert into dart_summary_imsi
    (  rcp_number, section, category, datas, comments )
    values (
      """ + str(row['rcp_number']) + """
    , '""" + str(row['section']) + """'
    , '""" + str(row['category']) + """'
    , '""" + str(row['values']) + """'
    , '""" + str(row['comment'].encode('utf-8').replace("'", "''").replace("&", "#")) + """'
    )
    """)
    print('=======================================================================================')
    print(SQL)
    curr.execute(SQL)
    conn.commit()
print('=======================================================================================')

try:
    curr.execute(""" drop table dart_summary """)
    conn.commit()
except:
    pass
curr.execute("""
    insert into dart_summary
    (  rcp_number, section, category, datas, comments )
    select distinct rcp_number, section, category, datas, comments
      from dart_summary_imsi
""")
conn.commit()

conn.close()

