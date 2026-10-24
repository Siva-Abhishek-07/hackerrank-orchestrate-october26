import sys
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/deletion_requests.csv')
subset = df_req[df_req['case_id'].isin([f"case_{i}" for i in range(530, 551)])]
for idx, r in subset.iterrows():
    print(f"[{r['case_id']}] {r['request_text']}")
