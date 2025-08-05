import os
import json
import urllib.request
import pandas as pd
import re
from pykrx import stock
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
from tqdm import tqdm
import time

class GetNewsUrl:
    def __init__(self, articles_per_stock=100):
        """초기화: API 키 로드 및 기본 설정"""
        load_dotenv()  # .env 파일 로드
        try:
            self.client_id = os.getenv('NAVER_CLIENT_ID')
            self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
            if not self.client_id or not self.client_secret:
                raise ValueError("API 키가 설정되지 않았습니다.")
        except Exception as e:
            print(f"API 키 로드 실패: {e}")
            self.client_id = "aa"
            self.client_secret = "aaa"

        self.articles_per_stock = articles_per_stock  # 종목당 수집할 기사 수
        self.stock_list_news = pd.DataFrame(columns=['article', 'title', 'link', 'summary', 'content', 'stock'])
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_stock_list(self,country):
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


#        codes = stock.get_index_portfolio_deposit_file("1028")
#        return [stock.get_market_ticker_name(code) for code in codes]

    def fetch_article_content(self, url):
        """주어진 URL에서 기사 본문 텍스트 추출"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.select_one("article#dic_area.go_trans._article_content")
            if content:
                return content.get_text(strip=True)
            else:
                print(f"기사 본문을 찾을 수 없습니다: {url}")
                return ""
        except requests.RequestException as e:
            print(f"기사 본문 요청 실패 ({url}): {e}")
            return ""

    def fetch_news_for_stock(self, stock):
        """특정 종목에 대한 뉴스 기사 수집"""
        print(f"\n=== {stock} 뉴스 기사 수집 ===")
        enc_text = urllib.parse.quote(stock)
        url = f"{self.base_url}?query={enc_text}&display={self.articles_per_stock}&sort=date"

        # API 요청 설정
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)

        try:
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                response_body = response.read()
                try:
                    data = json.loads(response_body.decode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류 ({stock}): {e}")
                    return

                # 뉴스 기사 처리
                items = data.get('items', [])
                if not items:
                    print(f"{stock}에 대한 뉴스 기사가 없습니다.")
                    return

                temp_data = []
                article_count = 0
                for i, item in enumerate(items, 1):
                    if 'naver.com' not in item['link']:
                        print(f"기사 {i} 제외: 네이버 링크 아님 ({item['link']})")
                        continue

                    # HTML 태그 제거
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

                    # 콘솔 출력
                    print(f"\n기사 {article_count}:")
                    print(f"제목: {title}")
                    print(f"링크: {item['link']}")
                    print(f"요약: {summary}")
                    print(f"본문: {content[:100]}..." if content else "본문: 없음")
                    print("-" * 50)

                    if article_count >= self.articles_per_stock:
                        break

                if temp_data:
                    self.stock_list_news = pd.concat(
                        [self.stock_list_news, pd.DataFrame(temp_data)], ignore_index=True
                    )
                else:
                    print(f"{stock}에 대한 네이버 뉴스 기사가 없습니다.")
            else:
                print(f"API 요청 실패 ({stock}) - Error Code: {response.getcode()}")
        except urllib.error.HTTPError as e:
            print(f"HTTP 오류 발생 ({stock}): {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f"URL 오류 발생 ({stock}): {e.reason}")
        except Exception as e:
            print(f"기타 오류 발생 ({stock}): {e}")

    def collect_all_news(self,country):
        """모든 종목에 대해 뉴스 수집"""
        stock_list = self.get_stock_list(country)
        for stock in stock_list:
            self.fetch_news_for_stock(stock)

    def save_to_csv(self, file_path="../data/news_data_america.csv"):
        """수집된 데이터를 CSV로 저장"""
        if not self.stock_list_news.empty:
            self.stock_list_news.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"데이터를 {file_path}에 저장했습니다.")
        else:
            print("저장할 데이터가 없습니다.")

    def run(self,country,file_path):
        """전체 프로세스 실행"""
        print("=== 뉴스 수집 시작 ===")
        self.collect_all_news(country)
        print("\n=== 최종 DataFrame ===")
        print(self.stock_list_news)
        self.save_to_csv(file_path)

if __name__ == "__main__":
    news_collector = GetNewsUrl(articles_per_stock=100)
    news_collector.run(country = 'america', file_path="../data/news_data_america.csv")