import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import os
from .function/keywords import *

st.set_page_config(layout="centered")

with st.sidebar:
    st.write('데이터 수집 과정')
    st.write('데이터 호출')
    st.write('뉴스기사 요약')

st.write('단순 뉴스 기사 호출')

# 데이터 검색

news = extract_news()
news.search_key


# 
st.header('뉴스 요약')
st.write('데모용 - openai로 구현')
long_text = df.loc['세금'].content.values[0]



with st.form("my_form"):
    api_key = ''
    client = OpenAI(api_key=api_key)  
    tools = [{
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia"
                }
            },
            "required": [
                "location"
            ],
            "additionalProperties": False
        }
    }]

    text = st.text_area(
        label = "Enter text:",
        value ='',
    )
    submitted = st.form_submit_button("Submit")
    if submitted:
        
        prompt = f'''
        아래 기사 내용에 대해서 다음과 같은 결과물을 내줘.
        이때, 결과물 형식에 제시한 형태로 내주어야 해
        
        * 작업 요청 내용
        1. 5줄로 요약해서 알려줘
        2. 주제
        3. 관련된 시장 현황

        * 결과물 형식
         1. 5줄 요약
         2. 주제
         3. 관련 시장 현황
         
        * 기사내용 : {text}

        '''
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": "너는 뉴스 기사 요약을 참 잘하는 전문가야"},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_output_tokens =1000
        )
        st.info('모델 결과')
        st.write(response.output[0].content[0].text)



