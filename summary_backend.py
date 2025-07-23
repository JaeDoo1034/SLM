import pandas as pd
from function.summary_function import NewsSummaryState
from function.summary_function import NewsSummaryAgent
from function.summary_function import build_summary_graph
from function.summary_function import summarize_article
from glob import glob


print("함수 import가 성공했습니다.")


file_list = glob('./data/*news.csv')
dfs = []
for item in file_list:
    df = pd.read_csv(item, encoding = 'utf-8-sig')
    dfs.append(df)

news_data = pd.concat(dfs)



print(news_data.head())
print(news_data['header'].head())
print(news_data['content'].head())
print(news_data['summary'].head())



