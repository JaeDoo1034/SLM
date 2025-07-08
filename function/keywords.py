import pandas as pd
import polars as pl
import duckdb

from openai import OpenAI # openAI API 활용 시
from langchain_openai import OpenAI # lanchain으로 컨버전 수행
from langchain_core.tools import tool # langchain으로 컨버전 수행

# ToDo 
# 1) function calling 대비용으로 함수 생성
# 2) re-ranking 을 사용하는 것까지 대비 필요


class DB_use():
    def __init__(self,dbname):
        self.dbname = dbname

    def Connect(self,table):
        table = f'{self.dbname}.db'
        con = duckdb.connect(database = table)
        con.execute('selec')