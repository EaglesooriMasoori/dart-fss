import psycopg2

conn = psycopg2.connect(database='stats', user='stats', password='stats')
curs = conn.cursor()
#########################################################################################################
#
# Table for ITEM list
#
#########################################################################################################
sql = """
create table item_base (
  item_code   varchar(10)
, item_name   varchar(100)
, constraint pk_item_base primary key (item_code)
)
"""
try:
    curs.execute("""drop table item_base""")
    conn.commit()
except:
    conn.rollback()
curs.execute(sql)
conn.commit()
#########################################################################################################
#
# Table for ITEM price
#
#########################################################################################################
sql = """
create table item_price (
  item_code         varchar(20)
, eod_date          char(8)
, eod_start_price   bigint
, eod_high_price    bigint
, eod_low_price     bigint
, eod_finish_price  bigint
, traded_count      bigint
, traded_amount     bigint
, total_amount      bigint
, constraint pk_eod_price primary key (item_code, eod_date)
)
"""
try:
    curs.execute("""drop table item_price""")
    conn.commit()
except:
    conn.rollback()
curs.execute(sql)
conn.commit()
#########################################################################################################
conn.close()
