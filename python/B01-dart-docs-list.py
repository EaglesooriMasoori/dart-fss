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

DART_KEY = str(sys.argv[1])
item_code = str(sys.argv[2])

url = "dart.fss.or.kr"
uri = "/api/search.xml"
params = {
    'auth': DART_KEY,
    'crp_cd': item_code,
    'start_dt': '19990101',
    'fin_rpt': 'Y',
    'dsp_tp': 'A',
    'page_set': '100'
}
html = BeautifulSoup(get_post(url, uri, params), "html.parser")
RCP_NO_LIST = []
for list in html.find_all('list'):
    RCP_NO_LIST.append({
        'crp_nm': list.find_all('crp_nm')[0].text,
        'rpt_nm': list.find_all('rpt_nm')[0].text,
        'rcp_no': list.find_all('rcp_no')[0].text,
        'rcp_dt': list.find_all('rcp_dt')[0].text
    })

print(RCP_NO_LIST)

for rcp_info in RCP_NO_LIST:
    print(rcp_info['rcp_no'])
    print(rcp_info['rpt_nm'])
    print(rcp_info['crp_nm'])
    print(rcp_info['rcp_dt'])
    rcp_no = rcp_info['rcp_no']


