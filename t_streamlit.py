import streamlit as st
from function.stock_data import get_today_yield
import asyncio
import os
## streamlit run t_streamlit.py

## slm_mcp 서버 실행
os.system('python slm_mcp/mcp_server.py &')

def test():

    print(get_today_yield("082640"))

print(test())

pg = st.navigation([st.Page("main.py"),st.Page("page_1.py"), st.Page("page_2.py"),st.Page('test.py')])
pg.run()
