import pandas as pd

df_req = pd.read_csv('dataset/deletion_requests.csv')
non_del = df_req[df_req['case_id'].isin([f'case_{i}' for i in range(533, 543)])]
for _, r in non_del.iterrows():
    print(r['case_id'], r['email'], r['requested_at'], r['reported_status'])
