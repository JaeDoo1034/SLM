from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
from google import genai
import vertexai
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import numpy as np
from tqdm import tqdm
from functools import partial

load_dotenv()

class AugDataLLM:
    def __init__(self,
                location:str = "us-central1",
                model_name = "gemini-2.5-flash-lite", #gemini-2.5-flash-lite
                **config_kwargs
                ):
        load_dotenv() # .env 파일에서 환경변수 로딩
        self.project_id = os.getenv("PROJECT_ID")

        if not self.project_id:
            raise ValueError("PROJECT_ID가 .env에 설정되어있지 않습니다.")
        
        vertexai.init(project="nimble-gate-464210-t4", location="us-central1")
        self.model_name = model_name
        self.model = GenerativeModel(model_name)

        # GenerationConfig 객체를 직접 생성하여 전달합니다.
        self.gen_config = GenerationConfig(
        temperature = config_kwargs.get("temperature", 0.3),
        top_p = config_kwargs.get("top_p", 0.95),
        max_output_tokens = config_kwargs.get("max_output_tokens", 10000),
        candidate_count = config_kwargs.get("candidate_count", 1),
)
    def _call_llm_stand_alone(self,prompt:str,**kwags) -> str:
        """
        llm 모델을 호출합니다.
        """
        contents = [prompt]
        response = self.model.generate_content(
            contents = contents,
            generation_config = self.gen_config,
        )
        return response.text

    def call_llm(self, row):
        prompt = f"""
        다음은 특정 종목에 대한 뉴스 기사입니다.

        <관련 종목명>: {row.stock}
        <뉴스 기사 본문>: {row.content}

        이 뉴스 본문을 바탕으로, 사용자가 해당 종목과 관련해 검색할 법만한 자연어 질문 1개를 생성하세요.
        - 질문은 기사에 명시적으로 언급된 내용과 관련되어야 합니다.
        - 정보 검색 목적에 맞도록 자연스럽고 구체적인 표현을 사용하세요.
        - 정보 검색 목적에 맞도록 자연스럽고 구체적인 표현을 사용하세요.
        - 질문은 짧고 명확해야 합니다. (예: "삼성전자의 반도체 매출 전망은?")
        - "어떻게", "왜", "무엇", "영향", "전망", "이유" 등의 키워드가 포함될 수 있습니다.
        
        출력 형식:
        query: 자연어 질문
        """
        return self._call_llm_stand_alone(prompt)
    
    def run_batch_parallel(self, df:pd.DataFrame, max_workers: int =4, batch_size = 8) -> pd.DataFrame:
        results = [None] * len(df) #결과저장 리스트
        for batch_start in range(0,len(df),batch_size):
            batch_end = min(batch_start + batch_size, len(df))
            batch_df = df.iloc[batch_start:batch_end]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.call_llm, row): idx + batch_start
                    for idx, row in enumerate(batch_df.itertuples(index=False))
                }

                for future in tqdm(as_completed(futures), total = len(futures), desc=f"Batch {batch_start//batch_size + 1}"):
                    idx = futures[future]
                    try:
                        output = future.result()
                        results[idx] = output.strip()
                    except Exception as e:
                        results[idx] = f"ERROR: {str(e)}"
        df["query"] = results
        return df                


if __name__ == "__main__":
    aug_data = AugDataLLM()
    df = pd.read_csv('../data/news_data.csv', encoding = 'utf-8-sig')
    df = df[['stock','content']]
    df = df.dropna(subset = ['content'])
    test_df = df.sample(n=100, random_state=42)
    result_df = aug_data.run_batch_parallel(test_df)
    result_df.to_csv('../data/test_set_250807.csv', encoding = 'utf-8-sig')

    
