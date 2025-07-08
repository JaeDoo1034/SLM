import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
st.set_page_config(layout="wide")
st.header('메인화면')
st.title('목차')
st.markdown('## page_1 :뉴스기사 보여주기 ')


html_code = """
<!DOCTYPE html>
<html>
  <head>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: true });
    </script>
  </head>
  <body>
    <div class="mermaid">
      graph LR;
      A[뉴스기사 크롤링] --> B[뉴스기사 표현];
      B --> C[종목별 뉴스기사 필터링];
      C --> D[요약 수행];
      D --> E[화면 구성];
    </div>
  </body>
</html>
"""

components.html(html_code, height=200)


st.markdown('## page_2  프로젝트 심화과정 ')
html_code = """
<!DOCTYPE html>
<html>
  <head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({ startOnLoad: true });
    </script>
  </head>
  <body>
    <div class="mermaid">
      graph LR
      A1[사용자 입력] --> A2[DB 조회 요청]
      A2 --> A3[문서 데이터 반환]

      subgraph RAG 구현 과정
        A3 --> B1[문서 임베딩]
        B1 --> B2[Vector DB 검색]
        B2 --> B3[관련 문서 선택]
        B3 --> B4[LLM 질의]
        B4 --> B5[응답 생성]
      end

      B5 --> C1[사용자에게 응답 표시]
    </div>
  </body>
</html>
"""

components.html(html_code, height=600, scrolling=True)

st.write('page_1 : 뉴스기사 보여주기 & 요약')
st.caption("단순 데모 용도")
st.caption(":blue[뉴스기사 보여주기용]:sunglasses:")