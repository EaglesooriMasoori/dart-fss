import win32com.client
import psycopg2

instCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
item_list = []
code_list = instCpCodeMgr.GetStockListByMarket(1) # KOSPI
for code in code_list:
    item_info = {
        'code':'P' + code
      , 'name':instCpCodeMgr.CodeToName(code)
    }
    item_list.append(item_info)
code_list = instCpCodeMgr.GetStockListByMarket(2) # KOSDAQ
for code in code_list:
    item_info = {
        'code':'Q' + code
      , 'name':instCpCodeMgr.CodeToName(code)
    }
    item_list.append(item_info)
conn = psycopg2.connect(database='stats', user='stats', password='stats')
curs = conn.cursor()
curs.execute(""" truncate table item_base """)
conn.commit()
for item in item_list:
    curs.execute("""
    insert into item_base
    ( item_code, item_name )
    values (
      '""" + item['code'] + """'
    , '""" + item['name'] + """'
    )
    """)
    conn.commit()
conn.close()
