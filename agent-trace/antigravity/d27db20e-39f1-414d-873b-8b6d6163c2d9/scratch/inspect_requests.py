import pandas as pd

df_req = pd.read_csv('dataset/deletion_requests.csv')
print(f"Total requests: {len(df_req)}")
print("Sample of request texts:")
for idx, r in df_req.head(20).iterrows():
    print(f"[{r['case_id']}] {r['request_text'][:100]}...")
