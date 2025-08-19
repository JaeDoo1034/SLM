### 필요 라이브러리 목록 ##

# 환경설정
import os
import sys
import time
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
# duckdb
import duckdb

# 데이터 전처리
import re
import pandas as pd
import numpy as np
import polars as pl
from datetime import datetime, timedelta
from copy import deepcopy

# 데이터 수집
import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
import nest_asyncio
nest_asyncio.apply()

# RDB 활용
import duckdb


# VectorDB 저장
from hashlib import md5
from langchain_community.vectorstores.utils import filter_complex_metadata # ChromaDB가 제공하지 못하는 데이터 형태를 자동으로 string처리
from datetime import datetime, timezone

## LLM 활용
#from summary_function import NewsSummaryAgent
# LLM 활용을 위한 dict형태 구축
from collections import defaultdict

# langchain 계열
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from langchain_openai import ChatOpenAI

# 1. LLM 모델 세팅 (OpenAI)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .summart_function_openai_2 import NewsSummaryAgent, build_summary_graph  # 너가 만든 것
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# ㄱRe-ranker 모델 활용
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder




# DB 저장/호출 기능
class ETF_DB():
    def __init__(self,path):
        self.path = path

    def Show_etf_top5(self):
        with duckdb.connect(self.path) as ETF_conn:
            ETF_df = ETF_conn.execute('select * from IRP_ETF_COMPOSE_table').fetchdf()
            # 전처리
            ETF_df = ETF_df.map(lambda x : x.strip())
            ETF_df_task_1 = ETF_df[ETF_df['구성종목 종목명'] != "설정현금액"]
            ETF_df_task_1 = ETF_df_task_1[ETF_df_task_1['구성종목 종목명'] != "원화현금"]
            ETF_df_task_1 = ETF_df_task_1[1:]
            # 원하는 컬럼 필터링
            ETF_df_task_2 = ETF_df_task_1[['ETF 종목명','구성종목 표준코드','구성종목 종목명','편입비율']]
            # 구성종목 중 상위 5개 추출
            ETF_df_task_3 = ETF_df_task_2.sort_values(by=['ETF 종목명','편입비율'], ascending=False)
            # 종목별 상위 5개
            ETF_df_task_4= ETF_df_task_3.groupby('ETF 종목명').head(5)
        return ETF_df_task_4


# 고객 데이터 DB 만들기
class Customer():
    def __init__(self,cus_path:str):
        self.path_cusDB = cus_path

    def get_cus_df(self,data:pd.DataFrame, tickers:list = ['ACE AI반도체포커스','ACE 2차전지&친환경차액티브','KODEX 자율주행액티브','RISE 200금융']):
        '''
        data : ETF 종목 정보가 담긴 데이터 프레임
        '''
        Customer_A = data[data['ETF 종목명'].isin(tickers)]

        # 전처리
        Customer_A = Customer_A.reset_index().drop('index',axis = 1)
        return Customer_A
    
    def get_ticker_lst(self,data:pd.DataFrame):
        '''
        목적 : 고객이 보유하고 있는 ETF 세부 종목의 리스트 추출.
        data : 고객이 보유하고 있는 ETF 종목이 담긴 데이터 프레임
        '''
        Custer_Having_ticker_lst = list(data['구성종목 종목명'].unique())
        return Custer_Having_ticker_lst
    
    def save_cus_df(self,data:pd.DataFrame):
        '''
        목적 : 고객이 보유하고 있는 ETF 종목이 담긴 데이터 프레임 저장
        data : 고객이 보유하고 있는 ETF 종목이 담긴 데이터 프레임
        '''
        with duckdb.connect(self.path_cusDB) as con :
            # Pandas DataFrame을 DuckDB에서 참조할 수 있도록 등록
            con.register('temp_df', data)

            # 테이블이 없다면 생성
            con.execute("""
                CREATE TABLE IF NOT EXISTS Customers AS
                SELECT * FROM temp_df LIMIT 0
            """)

            # 데이터 삽입
            con.execute("INSERT INTO Customers SELECT * FROM temp_df")
            print('DB Insert 완료!!')
            # 정리
            con.unregister('temp_df')
            print("저장 완료")





class Task_collect():

    path_cusnewsDB = 'DB/Customer_news.db'
    # 클래스변수 선언
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    
    # ▶ 기사 리스트 파싱 함수
    @staticmethod
    async def get_article_urls(session, page_url):
        try:
            async with session.get(page_url, headers=Task_collect.headers) as resp:
                text = await resp.text()
                soup = BeautifulSoup(text, 'html.parser')
                ul = soup.select_one('#content > div.left_cont > div > div.section.hk_news > div.section_cont > ul')
                if not ul:
                    return []

                urls = []
                for a in ul.find_all('a', href=True):
                    href = a['href']
                    if '/article/' in href:
                        urls.append(href)
                return list(set(urls))  # 중복 제거
        except Exception as e:
            print(f"[get_article_urls error] {page_url} - {e}")
            return []

    # ▶ 기사 상세 파싱 함수
    @staticmethod
    async def fetch_article(session, url):
        try:
            async with session.get(url, headers= Task_collect.headers) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')

                hostname = urlparse(url).hostname

                # ✅ 1. magazine.hankyung.com용 로직
                if 'magazine.hankyung.com' in hostname:
                    return {
                        'header': soup.select_one('#contents h1.news-tit').text.strip() if soup.select_one('#contents h1.news-tit') else None,
                        'summary': None,
                        'content': soup.select_one('#magazineView').text.strip() if soup.select_one('#magazineView') else None,
                        'url': url,
                        'datetime': soup.select_one('#contents span.txt-num').text.strip() if soup.select_one('#contents span.txt-num') else None,
                    }

                # ✅ 2. www.hankyung.com일 경우 기존 로직
                elif 'hankyung.com' in hostname:
                    return {
                        'header': soup.select_one('h1.headline').text.strip() if soup.select_one('h1.headline') else None,
                        'summary': soup.select_one('div.summary').text.strip() if soup.select_one('div.summary') else None,
                        'content': soup.select_one('#articletxt').text.strip() if soup.select_one('#articletxt') else None,
                        'url': url,
                        'datetime': soup.select_one('div.datetime span.txt-date').text.strip() if soup.select_one('div.datetime span.txt-date') else None,
                    }

                # ✅ 알 수 없는 도메인
                else:
                    print(f"⚠️ 알 수 없는 호스트: {hostname}")
                    return {'url': url, 'header': None, 'summary': None, 'content': None, 'datetime': None}

        except Exception as e:
            print(f"[fetch_article error] {url} - {e}")
            return {'url': url, 'header': None, 'summary': None, 'content': None, 'datetime': None}
    
    
    # ▶ 메인 비동기 루프
    @staticmethod
    async def extract_news_data_async(query_text, page_range):
        base_url = 'https://search.hankyung.com/search/news?query={query}&page={page}'
        search_urls = [base_url.format(query=query_text, page=p+1) for p in range(page_range)]

        async with aiohttp.ClientSession() as session:
            # 1. 페이지별 기사 링크 수집
            tasks = [Task_collect.get_article_urls(session, url) for url in search_urls]
            results = await asyncio.gather(*tasks)
            article_urls = list(set([url for sublist in results for url in sublist]))

            print(f"🔗 총 {len(article_urls)}개의 기사 URL 수집됨")

            # 2. 기사 본문 수집
            article_tasks = [Task_collect.fetch_article(session, url) for url in article_urls]
            articles = await asyncio.gather(*article_tasks)

            # 3. ticker 컬럼 추가
            for article in articles:
                article['ticker'] = query_text

            # 4. 비어 있으면 dummy row 추가
            if not articles:
                articles = [{
                    'header': None,
                    'summary': None,
                    'content': None,
                    'url': None,
                    'datetime': None,
                    'ticker': query_text
                }]
                print("⚠️ 수집된 기사가 없어 None 값으로 대체 저장합니다.")

            # 4. DuckDB 저장
            df = pd.DataFrame(articles)
            con = duckdb.connect('DB/Customer_news.db')

            # Pandas DataFrame을 DuckDB에서 참조할 수 있도록 등록
            con.register('temp_df', df)

            # 테이블이 없다면 생성
            con.execute("""
                CREATE TABLE IF NOT EXISTS articles AS
                SELECT * FROM temp_df LIMIT 0
            """)

            # 데이터 삽입
            con.execute("INSERT INTO articles SELECT * FROM temp_df")

            # 정리
            con.unregister('temp_df')
            con.close()

            print(f"✅ 저장 완료: DB/Customer_news.db (ticker = {query_text})")

    # ▶ 실행 함수
    @staticmethod
    def extract_news_data(query_text, page_range):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(Task_collect.extract_news_data_async(query_text, page_range))
    
    @staticmethod
    def save_news_df():
        with duckdb.connect(Task_collect.path_cusnewsDB) as cus_news:
                cusA_news_df = cus_news.execute('select * from articles').fetch_df()
                cusA_news_df = cusA_news_df.drop_duplicates()
        return cusA_news_df      


class Label():
    def __init__(self):
        pass

    @staticmethod
    def labeling(data:str,ticker:str):
        template = """
        <instruction>
        다음은 뉴스 기사 본문과 해당 기사에 매핑된 종목명(티커)입니다.
        당신의 임무는 기사 본문이 해당 종목에 대한 기사인지 여부를 판별하는 것입니다.

        규칙:
        - 1 : 뉴스 내용이 해당 종목의 시황을 나타낼 경우.
            예: 종목명이 기사에 등장하고, 그 종목의 실적, 주가, 제품, 사건, 경영, 산업 동향 등과 밀접한 관련이 있음.
            예) 종목의 실적/주가/사업/이슈/계약/정책/규제/소송/리스크/전망 등.
            예) 섹터 기사라도 해당 종목이 사례/주요 구성원으로 명시적 언급되고 맥락에 기여.
        - 0 : 뉴스 내용이 해당 종목을 단순 언급하는 경우이거나, 직접적으로 관련이 없음  
            예: 종목명이 전혀 등장하지 않거나, 비슷한 용어를 가진 단어의 내용이 등장하더라도 다른 주제가 메인인 경우.
            예) 피상적 나열(태그/키워드/꼬리말 광고)만 존재, 타사 이슈가 중심.
            
        출력 형식:
        - 숫자 1 또는 0만 출력
        </instruction>

        예시:
        ---
        [티커] 삼성전자
        [본문] 삼성전자가 2분기 실적 호조를 발표하며 주가가 3% 상승했다.
        [정답] 1
        ---
        [티커] 삼성전자
        [본문] 미국 증시가 기술주 중심으로 상승세를 보였다. 애플과 구글 주가가 상승했다.
        [정답] 0
        ---

        다음 데이터를 분류하세요.

        [티커] {ticker_name}
        [본문] {news_content}
        [정답]
        """

        prompt = ChatPromptTemplate.from_template(template)

        # 3. 체인 구성
        chain = prompt | llm | StrOutputParser()

        # 4. 실행 예시
        query = chain.invoke({"news_content": data,'ticker_name' : ticker})
        return query


class VectorDB():
    path = "VectorDB/chroma_news_db"
    
    @staticmethod
    def set_openai(embed_model:str,collection_name:str="SLM_News_openai"):
        openai_embedding = OpenAIEmbeddings(model=embed_model)
        vectordb_openai = Chroma(
        persist_directory=VectorDB.path,
        embedding_function=openai_embedding,
        collection_name=collection_name)
        return vectordb_openai
    
    @staticmethod
    def set_bge(embed_model:str,collection_name:str = "SLM_News_bge"):
        bge_embedding = HuggingFaceBgeEmbeddings(
            model_name=embed_model,
            model_kwargs={"device": "cpu"},          # "cpu" | "cuda" | "mps"
            encode_kwargs={"normalize_embeddings": True, "batch_size": 64}
            # query_instruction / embed_instruction는 기본적으로 생략 (M3는 보통 무지시로 OK)
        )
        vectordb_bge = Chroma(
        persist_directory=VectorDB.path,
        embedding_function=bge_embedding,
        collection_name=collection_name)
        return vectordb_bge
    
    @staticmethod
    def pick_splitter_by_length(text_len: int) -> RecursiveCharacterTextSplitter:
        """
        뉴스 본문의 길이에 따라 적절한 텍스트 분할기를 반환합니다.
        """
        if text_len <= 1200:
            # 짧은 기사 → 굳이 자르지 않고 1덩어리로 처리
            return RecursiveCharacterTextSplitter(
                chunk_size=1200,
                chunk_overlap=0,
                separators=["\n\n", "\n", " ", ""]
            )
        elif text_len <= 10_000:
            # 중간 길이 → 일반적인 1,200자 기준으로 분할
            return RecursiveCharacterTextSplitter(
                chunk_size=1200,
                chunk_overlap=150,
                separators=["\n\n", "\n", " ", ""]
            )
        elif text_len <= 50_000:
            # 긴 기사 → 덩어리를 좀 더 키움
            return RecursiveCharacterTextSplitter(
                chunk_size=1800,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
        else:
            # 초장문 → 더 크게 자르되, 요약도 고려 (이건 후속 처리 필요)
            return RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )


    # 2. 문서 리스트 생성 (chunk + metadata 포함)
    @staticmethod
    def make_documents(df):
        docs = []
        for idx, row in tqdm(df.iterrows()):
            text = row["content"]
            splitter = VectorDB.pick_splitter_by_length(len(text))
            chunks = splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                label = Label.labeling(chunks,row['stock'])
                metadata = {
                   "title": row["header"],
                    "url": row["url"],
                    "Date": row["Date"],
                    "ticker": row.get("stock", "None"),
                    "chunk_idx": i,
                    "original_idx": idx,
                    'label' : label  #labeling한 결과를 넣자!! 
                }
                time.sleep(0.1)
                docs.append(Document(page_content=chunk, metadata=metadata))

        return docs
    
    @staticmethod
    def make_doc_id(d: Document) -> str:
        """
        url + chunk_idx(없으면 0) + 시간
        """
        run_utc = datetime.now(timezone.utc)
        base = f"{d.metadata.get('url','')}_{d.metadata.get('chunk_idx', 0)}_{run_utc}"
        return md5(base.encode("utf-8")).hexdigest()
    
    @staticmethod
    def chunks(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i + size]


    @staticmethod
    def get_recent_articles(df: pd.DataFrame, ticker: str, days: int):
        df['Date'] = pd.to_datetime(df['Date'])
        today = df['Date'].max() # 가지고 있는 뉴스의 가장 최신 데이터
        recent_df = df[
            (df['ticker'] == ticker) &
            (df['Date'] >= today - timedelta(days=days))
        ]
        return recent_df.sort_values(by="Date", ascending=False)

    @staticmethod
    def save_vectordb(target_list:list,df:pd.DataFrame,kind:str,day:int=30):
        '''
        target_list : ticker 종목 리스트
        df : 뉴스 본문이 있는 데이터 프레임
        kind : 저장하고자 하는 벡터DB 
          > openai 임베딩 모델 : openai
          > bge-M3 임베딩 모델 : bge 
        day : 최신 날짜 기준으로 이전 N일치 기사 검색하는 기능.
        '''
        if kind == "openai":
            # collection_name : CustomerDB_Flow정리.ipynb 파일 기준으로 정리하다보니, SLM_News_1을 정함(직접 수집한 뉴스 데이터정보가 담겨있음)
            vectordb = VectorDB.set_openai(embed_model="text-embedding-3-large",collection_name='SLM_News_1')
        elif kind == "bge":
            vectordb = VectorDB.set_bge(embed_model="BAAI/bge-m3")
        else:
            raise "Not Exist that VectorDB"
        
        target_lst = target_list
        for ticker in target_lst:
            print(f"========= ticker {ticker} 진행 중~ =============")
            task_1_df = VectorDB.get_recent_articles(df,ticker=ticker,days = day)
            task_1_df['Date'] = task_1_df.Date.astype('str')
            task_1_df = task_1_df[task_1_df.stock==ticker]

            # document 만들기
            task_1_docs = VectorDB.make_documents(task_1_df)
            length_docs = len(task_1_docs)
            print(f'각 {ticker} 별 docs의 개수 : {length_docs}')
            BATCH = 64  # 상황에 맞게 조절

            for docs in tqdm(VectorDB.chunks(task_1_docs, BATCH), total=(len(task_1_docs) + BATCH - 1) // BATCH):

                ids = [VectorDB.make_doc_id(d) for d in docs]
                vectordb.add_documents(documents=docs, ids=ids)
                time.sleep(0.1) 

    def show_cnts(self,kind:str):
        '''
        kind : 저장하고자 하는 벡터DB 
          > openai 임베딩 모델 : openai
          > bge-M3 임베딩 모델 : bge 
        '''
        vectordb = ''
        if kind == "openai":
            # collection_name : CustomerDB_Flow정리.ipynb 파일 기준으로 정리하다보니, SLM_News_1을 정함(직접 수집한 뉴스 데이터정보가 담겨있음)
            vectordb = VectorDB.set_openai(embed_model="text-embedding-3-large",collection_name='SLM_News_1')
        elif kind == "bge":
            vectordb = VectorDB.set_bge(embed_model="BAAI/bge-m3")
        else:
            raise "Not Exist that VectorDB"
        print("Number of documents in DB:", vectordb._collection.count())
        

class cross_eval():
    '''
    목적 : cross-encoder 평가를 하기 위한 클래스
    '''
    @staticmethod
    def _dcg_at_k(labels, k=30):
        L = np.asarray(labels)[:k]
        if L.size == 0: return 0.0
        discounts = 1.0 / np.log2(np.arange(2, L.size + 2))
        return float(np.sum(L * discounts))
    
    @staticmethod
    def ndcg_at_k(labels, k=30):
        labels = np.asarray(labels)
        dcg  = cross_eval._dcg_at_k(labels, k)
        idcg = cross_eval._dcg_at_k(np.sort(labels)[::-1], k)
        return 0.0 if idcg == 0 else dcg / idcg
    
    @staticmethod
    def precision_at_k(labels, k=30):
        L = np.asarray(labels)[:k]
        return float(L.mean()) if L.size else 0.0
    
    @staticmethod
    def recall_at_k(labels, total_relevant, k=30):
        if not total_relevant or total_relevant <= 0: return 0.0
        return float(np.sum(np.asarray(labels)[:k])) / float(total_relevant)
    
    @staticmethod
    def mrr_at_k(labels, k=30):
        L = np.asarray(labels)[:k]
        hit = np.where(L > 0)[0]
        return 0.0 if hit.size == 0 else 1.0 / (hit[0] + 1)
    
    @staticmethod
    def map_at_k(labels, total_relevant, k=30):
        L = np.asarray(labels)[:k]
        if L.sum() == 0: return 0.0
        precisions, hit = [], 0
        for i, y in enumerate(L, start=1):
            if y:
                hit += 1
                precisions.append(hit / i)
        denom = max(1, min(total_relevant if total_relevant is not None else int(L.sum()), k))
        return float(np.sum(precisions) / denom)
    
    @staticmethod
    def eval_reranker_chunk(pool_df, ranked_df, k=30, rank_col="rank", score_col="relevance_score"):
        # 1) 풀: label만 필요 (score/rank 불필요)
        total_rel_pool = int(
            pd.to_numeric(pool_df["label"], errors="coerce").fillna(0).clip(0,1).sum()
        )
        print(f'total_rel_pool : {total_rel_pool}')

        # 2) 랭크드: 순서가 필요 (rank 우선, 없으면 score로 정렬, 둘 다 없으면 현재 순서 사용)
        g = ranked_df.copy()
        if rank_col in g.columns:
            g = g.sort_values(rank_col, ascending=True)
        elif score_col in g.columns:
            g = g.sort_values(score_col, ascending=False)
            g[rank_col] = np.arange(1, len(g)+1)
        else:
            g[rank_col] = np.arange(1, len(g)+1)

        y_topk = pd.to_numeric(g["label"], errors="coerce").fillna(0).clip(0,1).astype(int).values[:k]
        print(f'y_topk : {y_topk}')
        return {
            f"Precision@{k}": cross_eval.precision_at_k(y_topk, k),
            f"Recall@{k}(pool)": cross_eval.recall_at_k(y_topk, total_rel_pool, k),
            f"MRR@{k}": cross_eval.mrr_at_k(y_topk, k),
            f"MAP@{k}": cross_eval.map_at_k(y_topk, total_rel_pool, k),
            f"nDCG@{k}": cross_eval.ndcg_at_k(y_topk, k),
            "PoolSize": int(len(pool_df)),
            "PoolRelevant": total_rel_pool,
            "TopK": int(min(len(g), k)),
            "TopKRelevant": int(y_topk.sum()),
        }




class Test():
    def __init__(self):
        pass
    
    @staticmethod
    def total_data(kind:str) -> pd.DataFrame:
        '''
        kind : 저장하고자 하는 벡터DB 
          > openai 임베딩 모델 : openai
          > bge-M3 임베딩 모델 : bge 
        '''
        vectordb = ''
        if kind == "openai":
            # collection_name : CustomerDB_Flow정리.ipynb 파일 기준으로 정리하다보니, SLM_News_1을 정함(직접 수집한 뉴스 데이터정보가 담겨있음)
            vectordb = VectorDB.set_openai(embed_model="text-embedding-3-large",collection_name='SLM_News_1')
        elif kind == "bge":
            vectordb = VectorDB.set_bge(embed_model="BAAI/bge-m3")
        else:
            raise "Not Exist that VectorDB"

        VecDB = vectordb._collection
        total_results = VecDB.get(
         include = ['documents','metadatas']   
        )
        total_df = pd.DataFrame(total_results['metadatas'])
        return total_df

    @staticmethod
    def set_before_df(ticker_list:list,kind:str) -> pd.DataFrame:
        target_list = ticker_list
        '''
        kind : 저장하고자 하는 벡터DB 
          > openai 임베딩 모델 : openai
          > bge-M3 임베딩 모델 : bge 
        '''
        vectordb = ''
        if kind == "openai":
            # collection_name : CustomerDB_Flow정리.ipynb 파일 기준으로 정리하다보니, SLM_News_1을 정함(직접 수집한 뉴스 데이터정보가 담겨있음)
            vectordb = VectorDB.set_openai(embed_model="text-embedding-3-large",collection_name='SLM_News_1')
        elif kind == "bge":
            vectordb = VectorDB.set_bge(embed_model="BAAI/bge-m3")
        else:
            raise "Not Exist that VectorDB"

        before_lst = []
        for ticker in target_list:
            retriever = vectordb.as_retriever(search_kwargs={"k": 30,'filter' : {'ticker' : ticker}})
            CrossEncoder_prompt = f'''
            이 뉴스들 중에서 "{ticker}"가 핵심 주제로 다뤄진 기사만 알려줘.
            다른 회사 언급이 많거나, {ticker}가 단순히 함께 언급된 기사라면 제외해줘.
            '''
            print(CrossEncoder_prompt.strip())
            raw_docs = retriever.get_relevant_documents(CrossEncoder_prompt)
            before_lst.extend(raw_docs)
            print(list(map(lambda x: x.metadata['label'],raw_docs))[:5])
            print(list(map(lambda x: x.page_content,raw_docs))[:5])

        rerank_df_before = pd.DataFrame(list(map(lambda x: x.metadata,before_lst)))
        return rerank_df_before
    
    @staticmethod
    def reranker_model(k:int=30):
        model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
        compressor = CrossEncoderReranker(model=model, top_n=k)
        #print(compressor)
        return compressor
    

    def eval_test(self,ticker_list:list,kind:str,state:str,total:str=None):
        '''
        kind : 저장하고자 하는 벡터DB 
          > openai 임베딩 모델 : openai
          > bge-M3 임베딩 모델 : bge 

        state : reranker 모델 활용 여부를 구분하기 위함
          > reranker 사용 X : No
              - No 일때는 total 입력 불필요.
          > reranker 사용 O : Yes

        total : 종목별 문건을 reranker 모델을 적용하는 것인지, 전체 문건 대상으로 ranker모델 적용하는 것인지 확인.
          > 종목별로 문건을 비교 : seg
          > 전체 문건 대상으로 비교 : tot
        '''
        total_df = ''
        if kind == "openai":
            total_df = Test.total_data(kind=kind)
           # collection_name : CustomerDB_Flow정리.ipynb 파일 기준으로 정리하다보니, SLM_News_1을 정함(직접 수집한 뉴스 데이터정보가 담겨있음)
            vectordb = VectorDB.set_openai(embed_model="text-embedding-3-large",collection_name='SLM_News_1')
        elif kind == "bge":
            vectordb = VectorDB.set_bge(embed_model="BAAI/bge-m3")
        else:
            raise "Not Exist that VectorDB"

        target_lst = ticker_list


        # Test 방식 세분화
        ## 1. Reranker 모델 사용 전.
        if state == 'No':
            before_df = Test.set_before_df(kind=kind,ticker_list=target_lst)

            # 결과 모음.
            eval_lst = []
            for stock in target_lst:
                total_df_target = total_df[total_df.ticker==stock]
                rerank_df_target = before_df[before_df.ticker==stock]
                eval_lst.append(cross_eval.eval_reranker_chunk(total_df_target,rerank_df_target))
            

            eval_set_df = dict(zip(target_lst,eval_lst))
            eval_df = pd.DataFrame(eval_set_df)
            return eval_df
        
        ## 2. rerank모델 활용 & 전체 문건 대상으로 모델 적용
        elif (state == 'Yes') & (total == 'tot') :
            # 모델 불러오기.
            model = Test.reranker_model(k=30)

            scored_docs = []
            for ticker in target_lst[:10]:
                retriever = vectordb.as_retriever(search_kwargs={"k": 50})
                CrossEncoder_prompt = f'''
                이 뉴스들 중에서 "{ticker}"가 핵심 주제로 다뤄진 기사만 알려줘.
                다른 회사 언급이 많거나, {ticker}가 단순히 함께 언급된 기사라면 제외해줘.
                '''
                print(CrossEncoder_prompt.strip())
                raw_docs = retriever.get_relevant_documents(CrossEncoder_prompt)
                pairs = [(CrossEncoder_prompt, d.page_content) for d in raw_docs]
                scores = model.score(pairs)

                # 3) 점수 붙이고 재정렬
                for d, s in zip(raw_docs, scores):
                    dd = deepcopy(d)
                    dd.metadata["relevance_score"] = float(s)
                    scored_docs.append(dd)

            rerank_df = pd.DataFrame(list(map(lambda x: x.metadata,scored_docs)))
            rerank_df= rerank_df.sort_values(by=['ticker','relevance_score'],ascending=False)

            rerank_eval = []
            for kind in target_lst:
                total_df_target = total_df[total_df.ticker==kind]
                rerank_df_target = rerank_df[rerank_df.ticker==kind]
                rerank_eval.append(cross_eval.eval_reranker_chunk(total_df_target,rerank_df_target))
            rerank_eval_con = dict(zip(target_lst,rerank_eval))
            rerank_eval_df = pd.DataFrame(rerank_eval_con)
            return rerank_eval_df
        
         ## 3. rerank모델 활용 & 종목별 문건 대상으로 모델 적용
        elif (state == 'Yes') & (total == 'seg') :
            # 모델 불러오기.
            model = Test.reranker_model(k=30)

            scored_docs = []
            for ticker in target_lst[:10]:
                retriever = vectordb.as_retriever(search_kwargs={"k": 50,'filter' : {'ticker' : ticker}})
                CrossEncoder_prompt = f'''
                이 뉴스들 중에서 "{ticker}"가 핵심 주제로 다뤄진 기사만 알려줘.
                다른 회사 언급이 많거나, {ticker}가 단순히 함께 언급된 기사라면 제외해줘.
                '''
                print(CrossEncoder_prompt.strip())
                raw_docs = retriever.get_relevant_documents(CrossEncoder_prompt)
                pairs = [(CrossEncoder_prompt, d.page_content) for d in raw_docs]
                scores = model.score(pairs)

                # 3) 점수 붙이고 재정렬
                for d, s in zip(raw_docs, scores):
                    dd = deepcopy(d)
                    dd.metadata["relevance_score"] = float(s)
                    scored_docs.append(dd)

            rerank_df = pd.DataFrame(list(map(lambda x: x.metadata,scored_docs)))
            rerank_df= rerank_df.sort_values(by=['ticker','relevance_score'],ascending=False)

            rerank_eval = []
            for kind in target_lst:
                total_df_target = total_df[total_df.ticker==kind]
                rerank_df_target = rerank_df[rerank_df.ticker==kind]
                rerank_eval.append(cross_eval.eval_reranker_chunk(total_df_target,rerank_df_target))
            rerank_eval_con = dict(zip(target_lst,rerank_eval))
            rerank_eval_df = pd.DataFrame(rerank_eval_con)
            return rerank_eval_df
        
    @staticmethod
    def get_full_article_from_chroma(original_idx: int,kind:str, ticker : str) -> dict:
        """original_idx 기준으로 chunk들을 모아 원문 복원"""
        # 1. 해당 article의 모든 chunk 가져오기
        vectordb = ''
        if kind == "openai":
            # collection_name : CustomerDB_Flow정리.ipynb 파일 기준으로 정리하다보니, SLM_News_1을 정함(직접 수집한 뉴스 데이터정보가 담겨있음)
            vectordb = VectorDB.set_openai(embed_model="text-embedding-3-large",collection_name='SLM_News_1')
        elif kind == "bge":
            vectordb = VectorDB.set_bge(embed_model="BAAI/bge-m3")
        else:
            raise "Not Exist that VectorDB"
        
        
        VecDB = vectordb._collection
        results = VecDB.get(
        where = { "$and" : [ # 빈 쿼리로 전체 탐색
                {"original_idx": original_idx}, 
                {"ticker": ticker}
                ]
            },
            include = ['documents','metadatas']   
            )
            
        if not results:
            return {"error": f"No chunks found for original_idx {original_idx}"}

        #print(results)
        #print(results['metadatas'][0]['chunk_idx'])

        # 4. 대표 metadata 하나 뽑아 저장
        return {
            "title": results['metadatas'][0]["title"],
            "url": results['metadatas'][0]["url"],
            "Date": results['metadatas'][0]["Date"],
            "ticker": results['metadatas'][0]["ticker"],
            "content": results['documents'][0]
        }
    
    @staticmethod
    def get_original_news_after_reranker(ticker:str,kind:str):
        '''
        kind : 저장하고자 하는 벡터DB 
          > openai 임베딩 모델 : openai
          > bge-M3 임베딩 모델 : bge 
        '''
        vectordb = ''
        if kind == "openai":
            # collection_name : CustomerDB_Flow정리.ipynb 파일 기준으로 정리하다보니, SLM_News_1을 정함(직접 수집한 뉴스 데이터정보가 담겨있음)
            vectordb = VectorDB.set_openai(embed_model="text-embedding-3-large",collection_name='SLM_News_1')
        elif kind == "bge":
            vectordb = VectorDB.set_bge(embed_model="BAAI/bge-m3")
        else:
            raise "Not Exist that VectorDB"

        CrossEncoder_prompt_test = f'''
        이 뉴스들 중에서 "{ticker}"가 핵심 주제로 다뤄진 기사만 알려줘.
        다른 회사 언급이 많거나, {ticker}가 단순히 함께 언급된 기사라면 제외해줘.
        '''
        #print(CrossEncoder_prompt_test)
        retriever = vectordb.as_retriever(search_kwargs={"k": 50,'filter' : {'ticker' : ticker}})
        compressor= Test.reranker_model(k=30)
        #print('COM : ',compressor)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

        compressed_docs = compression_retriever.invoke(CrossEncoder_prompt_test)
        original_idxs = list(map(lambda x: x.metadata['original_idx'], compressed_docs))
        top_n_original = [Test.get_full_article_from_chroma(idx,ticker=ticker,kind =kind) for idx in original_idxs]

        original_contents = list(map(lambda x: x['content'],top_n_original))
        total_contents = ''.join(original_contents)
        return total_contents

    
    def summarize_top_articles_after_reranker(self,total_contents,ticker:str,max_iters:int) -> pd.DataFrame:
        '''
        total_contents : get_original_news_after_reranker 결과 값을 input으로!
        ticker : 종목명
        max_iters : LLM_AS_JUDGE 판단 횟수
        '''
        
        agent = NewsSummaryAgent(max_iters=max_iters)
        runnable = build_summary_graph(agent)

        rows = []
        doc = total_contents

        state = {"article": doc, "summary": "", "feedback": "", "iteration": 0}
        result = runnable.invoke(state)

        print("✅ 실행 결과 키:", result.keys())
        # 여기서 final_summary 반드시 존재해야 함(위 패치 기준)
        final_summary = result.get("final_summary")
        if not final_summary:
            print("❌ final_summary 없음. 디버그용 전체 상태:", result)
            # 계속 진행할지, 실패로 표기할지 선택

        rows.append({
            "ticker": ticker,
            "date": '2025-07-30', # 위 조회 기준일자로 연동시켜서 바꿀 예정
            "summary": final_summary,
            "feedback": result.get("last_feedback", "피드백 없음"),
        })

        return pd.DataFrame(rows)

