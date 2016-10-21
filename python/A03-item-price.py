# -*- coding: utf-8 -*-
import win32com.client
import psycopg2

def get_item_price(p_item_code, date_count):
    instStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    '''
    0 :: 종목 코드   :: 요청할 종목의 종목 코드
    1 :: 요청 구분   :: ‘1’: 기간으로 요청, ‘2’: 갯수로 요청
    2 :: 요청 종료일 :: YYYYMMDD 형식
    3 :: 요청 시작일 :: YYYYMMDD 형식
    4 :: 요청 개수   :: 요청할 데이터의 개수
    5 :: 필드
        ::
            0: 날짜   ,  1: 시간
            2: 시가   ,  3: 고가
            4: 저가   ,  5: 종가
            6: 전일대비,  8: 거래량
            9: 거래대금, 10: 누적체결매도수량, 13:시가총액
    6 :: 차트 구분   :: ‘D’: 일, ‘W’: 주, ‘M’: 월, ‘m’: 분, ‘T’: 틱
    9 :: 수정 주가   :: ‘0’: 무수정주가, ‘1’: 수정주가
    '''
    instStockChart.SetInputValue(0, p_item_code)
    instStockChart.SetInputValue(1, ord('2'))
    instStockChart.SetInputValue(4, date_count)
    instStockChart.SetInputValue(5, (0, 2, 3, 4, 5, 8, 9, 13))
    instStockChart.SetInputValue(6, ord('D'))
    instStockChart.SetInputValue(9, ord('1'))
    instStockChart.BlockRequest()
    # GET ROW, COLUMN COUNT
    # col_count = instStockChart.GetHeaderValue(1)
    row_count = instStockChart.GetHeaderValue(3)
    table_data = []
    for i in range(row_count):
        row = {
              'item_code': p_item_code
            , 'eod_date': str(instStockChart.GetDataValue(0, i))
            , 'eod_start_price': str(instStockChart.GetDataValue(1, i))
            , 'eod_high_price': str(instStockChart.GetDataValue(2, i))
            , 'eod_low_price': str(instStockChart.GetDataValue(3, i))
            , 'eod_finish_price': str(instStockChart.GetDataValue(4, i))
            , 'traded_count': str(instStockChart.GetDataValue(5, i))
            , 'traded_amount': str(instStockChart.GetDataValue(6, i))
            , 'total_amount': str(instStockChart.GetDataValue(7, i))
        }
        table_data.append(row)
    return table_data

base_item_code = 'A005930'
price_list = get_item_price(base_item_code, 1100)

conn = psycopg2.connect(database='stats', user='stats', password='stats')
curs = conn.cursor()
curs.execute("""
delete from item_price
 where item_code = '""" + base_item_code + """'
""")
conn.commit()
for row in price_list:
    curs.execute("""
    insert into item_price
    (
      item_code
    , eod_date
    , eod_start_price
    , eod_high_price
    , eod_low_price
    , eod_finish_price
    , traded_count
    , traded_amount
    , total_amount
    ) values (
      '""" + row['item_code'] + """'
    , '""" + row['eod_date'] + """'
    , """ + row['eod_start_price'] + """
    , """ + row['eod_high_price'] + """
    , """ + row['eod_low_price'] + """
    , """ + row['eod_finish_price'] + """
    , """ + row['traded_count'] + """
    , """ + row['traded_amount'] + """
    , """ + row['total_amount'] + """
    )
    """)
    conn.commit()
conn.close()
