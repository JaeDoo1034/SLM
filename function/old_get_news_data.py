import os
import json
import sys
import urllib.error
import urllib.request
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import requests
from bs4 import BeautifulSoup
from pykrx import stock
from dotenv import load_dotenv
import FinanceDataReader as fdr
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class GetNewsData:
    def __init__(self, articles_per_stock = 100, max_workers=5, batch_size = 20):
        logging.basicConfig(
            filename="news_collector.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        """
        초기화: API 키 로드 및 기본 설정
        """
        # .env 파일 로드
        load_dotenv()
        # 네이버 API 클라이언트 정보
        # 각자의 뉴스 api를 사용해주세요
        try:
            self.client_id = os.getenv('NAVER_CLIENT_ID')
            self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
            if not self.client_id or not self.client_secret:
                raise ValueError("API 키가 설정되지 않았습니다.")
        except Exception as e:
            print(f"API Key 로드 실패: {e}")
            self.client_id = "aa"
            self.client_secret = "aa"

        self.articles_per_stock = articles_per_stock
        self.max_workers = max_workers
        self.batch_size = batch_size # 배치 크기 추가
        self.stock_list_news = pd.DataFrame(columns=['article', 'title', 'link', 'summary', 'content','stock'])
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_stock_list(self, country:str):
        """
        country: 미국, 한국 등 주식 시장을 정해줍니다.
         - america, korea
        code: 주식시장의 code
        """

        if country.lower() == 'korea':
            """
            한국 종목명 수집
            """
            stock_ids = '1028' # 기획에 따라 Kospi 이외의 종목도 수집합니다.
            codes = stock.get_index_portfolio_deposit_file(stock_ids)
            code_li = [stock.get_market_ticker_name(code) for code in codes]
            return code_li
        
        elif country.lower() == 'america':
            """
            미국 종목명 수집
            """
            market_li = ['NASDAQ','NYSE']
            code_li = []
            for market in market_li:
                stocks = fdr.StockListing(market)
                code_li.extend(stocks['Name'].tolist()) # list flatten
            return code_li
        else:
            raise ValueError("지원하지 않는 국가입니다: 'korea' 또는 'america'만 가능")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.RequestException)
    )

    def fetch_article_content(self, url):
        """주어진 URL에서 기사 본문 텍스트 추출"""
        try:
            response = requests.get(url, headers = self.headers, timeout = 5)
            time.sleep(0.2)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.select_one("article#dic_area.go_trans._article_content")
            if content:
                return content.get_text(strip=True)
            else:
                print(f'기사 본문을 찾을 수 없습니다: {url}')
                return ""
        except requests.RequestException as e:
            print(f'기사 본문 요청 실패({url}): {e}')
            return ""
    @retry(
        stop=stop_after_attempt(3),  # 최대 3번 재시도
        wait=wait_exponential(multiplier=1, min=4, max=10),  # 지수 백오프
        retry=retry_if_exception_type((urllib.error.HTTPError, requests.RequestException))
    )    
           
    def fetch_news_for_stock(self, stock):
        logging.info(f"Starting news collection for {stock}")
        """특정 종목에 대한 뉴스 기사 수집"""
        print(f"\n=== {stock} 뉴스 기사 수집 ===")
        enc_text = urllib.parse.quote(stock)
        url = f"{self.base_url}?query={enc_text}&display={self.articles_per_stock}&sort=date"
        #API 요청 설정
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)

        temp_data = []
        try:
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                response_body = response.read()
                try:
                    data = json.loads(response_body.decode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류({stock}: {e})")
                    return temp_data
                
                # 뉴스기사처리
                items = data.get('items', [])
                if not items:
                    print(f"{stock}에 대한 뉴스가 없습니다.")
                    return temp_data
                
                article_count = 0
                for i, item in enumerate(items, 1):
                    if 'naver.com' not in item['link']:
                        print(f"기사 {i} 제외: 네이버 링크 아님 ({item['link']})")
                        continue

                    #HTML 태그 제거
                    title = re.sub(r'<[^>]+>', '', item['title'])
                    summary = re.sub(r'<[^>]+>', '', item['description']) 
                    # 기사 본문 추출
                    content = self.fetch_article_content(item['link'])

                    temp_data.append({
                        'article': f"{stock}_{article_count + 1}",
                        'title': title,
                        'link': item['link'],
                        'summary': summary,
                        'content': content,
                        'stock': stock
                    })
                    article_count += 1

                    # Console 출력
                    print(f"\n기사 {article_count}:")
                    print(f"제목: {title}")
                    print(f"링크: {item['link']}")
                    print(f"요약: {summary}")
                    print("-" * 50)

                    if article_count >= self.articles_per_stock:
                        break
            else:
                print(f"API 요청 실패 ({stock}) - Error Code: {response.getcode()}")
        
        except urllib.error.HTTPError as e:
            print(f"HTTP 오류 발생 ({stock})")
        except urllib.error.URLError as e:
            print(f"URL 오류 발생 ({stock}: {e.reason})")
        except Exception as e:
            print(f"기타 오류 발생 ({stock}: {e})")
        finally:
            time.sleep(0.5)
        return temp_data
        
    def collect_all_news(self,country:str):
        """
        모든 종목에 대한 뉴스 수집 (배치처리)
        """
        stock_list = self.get_stock_list(country)
        total_stocks = len(stock_list)
        print(f'총 {total_stocks}개 종목을 처리합니다.')

        #배치 단위로 처리
        for i in range(0, total_stocks, self.batch_size):
            batch = stock_list[i:i + self.batch_size]
            print(f"\n=== 배치 {i // self.batch_size + 1} 처리 종목 {i +1 } ~ {min(i + self.batch_size, total_stocks)}) ===")
            
            with ThreadPoolExecutor(max_workers = self.max_workers) as executor:
                # 각 종목에 대해 fetch_news_for_stock 실행
                future_to_stock = {executor.submit(self.fetch_news_for_stock, stock):
                stock for stock in batch}

                for future in tqdm(as_completed(future_to_stock), total = len(batch), desc=f"배치 {i // self.batch_size + 1} 뉴스 수집"):
                    stock = future_to_stock[future]
                    try:
                        temp_data = future.result()
                        if temp_data:
                            self.stock_list_news = pd.concat(
                                [self.stock_list_news, pd.DataFrame(temp_data)], ignore_index=True
                            )
                    except Exception as e:
                        print(f'Thread 처리 중 오류 발생({stock}: {e})')
            time.sleep(2) # 배치 간 1초 대기 (API 제한 방지)

    def save_to_csv(self, file_path = "../data/news_data_america.csv"):
        """
        수집 데이터를 csv로 저장
        """
        if not self.stock_list_news.empty:
            self.stock_list_news.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"데이터를 {file_path}에 저장했습니다.")
        else:
            print("저장할 데이터가 없습니다.")
    
    def run(self, country = 'korea'):
        """전체 프로세스 실행"""
        print("=== 뉴스 수집 시작===")
        start_time = time.time()
        self.collect_all_news(country)
        end_time = time.time()
        print(f"\n===뉴스 수집 완료 (소요 시간: {end_time - start_time:.2f}초) ===")
        print(f'\n===최종 DataFrame ===')
        print(self.stock_list_news)
        self.save_to_csv()

if __name__ == '__main__':
    news_collector = GetNewsData(articles_per_stock=100,max_workers=5,batch_size=20)
    news_collector.run(country = 'america')