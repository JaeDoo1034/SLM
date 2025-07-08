import streamlit as st

import os 
import sys

pg = st.navigation([st.Page("main.py"),st.Page("page_1.py"), st.Page("page_2.py"),st.Page('test.py')])
pg.run()


