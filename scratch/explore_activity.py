import pandas as pd
import re

df_act = pd.read_csv('dataset/system_activity.csv')
print(f"Total rows in system_activity: {len(df_act)}")
print(f"Columns: {list(df_act.columns)}")
print("\nUnique event types:")
print(df_act['event_type'].value_counts())
print("\nUnique source systems:")
print(df_act['source_system'].value_counts())
print("\nUnique target systems:")
print(df_act['target_system'].value_counts())
print("\nUnique reported results:")
print(df_act['reported_result'].value_counts())

# Check how details field looks
print("\nSample details:")
for d in df_act['details'].dropna().head(20):
    print(" -", d)
