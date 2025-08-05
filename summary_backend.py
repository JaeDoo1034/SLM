import pandas as pd
from function.summary_function import NewsSummaryState
from function.summary_function import NewsSummaryAgent
from function.summary_function import build_summary_graph
from function.summary_function import summarize_article
from glob import glob
import ast


print("함수 import가 성공했습니다.")

agent = NewsSummaryAgent()
runnable = build_summary_graph(agent)


file_list = glob('./data/*news.csv')
dfs = []
for item in file_list:
    df = pd.read_csv(item, encoding = 'utf-8-sig')
    dfs.append(df)

news_data = pd.concat(dfs)
# input content
sample_news = pd.DataFrame({'article':news_data['content'][500:]})
results = agent.run_batch_parallel(sample_news, max_workers=3)
#output summary
result_df = pd.DataFrame({'summary_result':results})
#result_df['modified_data'] = result_df['summary_result'].apply(lambda x: ast.literal_eval(x))
result_df.to_csv('sample_result_final.csv', encoding = 'utf-8-sig')
 