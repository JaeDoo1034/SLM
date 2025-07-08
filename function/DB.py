import duckdb
import pandas as pd
import os
import sys

## 1. 뉴스기사 db로 저장하기
## -- 지금은 file 형태에서 바로 가져오는 걸로 짜보자
with duckdb.connect('../DB/news.db') as news_con:
    ## 아래는 Todo : 뉴스 크롤링하면서 그 정보를 json 형태로 가져오고 난 이후, 그 정보를 DB 에 저장
    ## sudo...

    
    ## 지금은 File에서 바로 DB 테이블로 저장
    file_path = '../data/{}.csv'
    try:
        df_1 = pd.read_csv(file_path.format(경제정책),index_col=[0],encoding='utf-8-sig')
        df_2 = pd.read_csv(file_path.format(거시경제),index_col=[0],encoding='utf-8-sig')
        df_3 = pd.read_csv(file_path.format(고용복지),index_col=[0],encoding='utf-8-sig')
        df_4 = pd.read_csv(file_path.format(세금),index_col=[0],encoding='utf-8-sig')
        df_5 = pd.read_csv(file_path.format(외환시장),index_col=[0],encoding='utf-8-sig')

        # 임시 테이블 등록하기
        news_con.register("df_1", df_1)
        news_con.register("df_2", df_2)
        news_con.register("df_3", df_3)
        news_con.register("df_4", df_4)
        news_con.register("df_5", df_5)

        # 테이블 저장 
        news_con.execute("CREATE TABLE 거시경제_table AS SELECT * FROM df_1")
        news_con.execute("CREATE TABLE 외환시장_table AS SELECT * FROM df_2")
        news_con.execute("CREATE TABLE 경제정책_table AS SELECT * FROM df_3")
        news_con.execute("CREATE TABLE 세금_table AS SELECT * FROM df_4")
        news_con.execute("CREATE TABLE 고용복지_table AS SELECT * FROM df_5")
    except:
        print('이미 존재')
    #print(news_con.execute('select * from 거시경제_table').fetchdf())


## 2. 퇴직연금 구성 정보 DB 구성
with duckdb.connect('../DB/ETF.db') as ETF_con:
    # ETF File
    IRP_ETF_compose = pd.read_excel('../data/IRP_ETF_구성종목.xlsx')
    IRP_ETF = pd.read_excel('../data/IRP_ETF.xlsx')

    # 임시 등록
    ETF_con.register("df_1", IRP_ETF_compose)
    ETF_con.register("df_2", IRP_ETF)
    
    
    ETF_con.execute("CREATE TABLE IRP_ETF_COMPOSE_table AS SELECT * FROM df_1")
    ETF_con.execute("CREATE TABLE IRP_ETF_table AS SELECT * FROM df_2")