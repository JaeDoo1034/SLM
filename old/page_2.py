import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import os

st.set_page_config(layout="centered")

with st.sidebar:
    st.write('데이터 수집 과정')
    st.write('데이터 호출')
    st.write('뉴스기사 요약')

st.write('단순 뉴스 기사 호출')

# 데이터 호출
# 시황 데이터
df_1 = pd.read_csv('data/거시경제_news.csv',index_col=[0],encoding='utf-8-sig')
df_2 = pd.read_csv('data/외환시장_news.csv',index_col=[0],encoding='utf-8-sig')
df_3 = pd.read_csv('data/경제정책_news.csv',index_col=[0],encoding='utf-8-sig')
df_4 = pd.read_csv('data/세금_news.csv',index_col=[0],encoding='utf-8-sig')
df_5 = pd.read_csv('data/고용복지_news.csv',index_col=[0],encoding='utf-8-sig')

df = pd.concat([df_1,df_2,df_3,df_4,df_5],axis = 0).set_index('kind')

# 데이터 노출
st.header('시황')
radio_stauts = st.radio(label='선택', options = set(list(df.index)),horizontal =True)
if radio_stauts == '세금':
    st.dataframe(df.loc['세금'],use_container_width=True,hide_index=True)
if radio_stauts == '고용복지':
    st.dataframe(df.loc['고용복지'],use_container_width=True,hide_index=True)
if radio_stauts == '외환시장':
    st.dataframe(df.loc['외환시장'],use_container_width=True,hide_index=True)
if radio_stauts == '거시경제':
    st.dataframe(df.loc['거시경제'],use_container_width=True,hide_index=True)
if radio_stauts == '경제정책':
    st.dataframe(df.loc['경제정책'],use_container_width=True,hide_index=True)



st.header('뉴스 요약')
st.write('데모용 - openai로 구현')
long_text = df.loc['세금'].content.values[0]



with st.form("my_form"):
    api_key = '';
    client = OpenAI(api_key=api_key)  
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



