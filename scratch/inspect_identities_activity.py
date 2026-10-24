import pandas as pd
import re

df_act = pd.read_csv('dataset/system_activity.csv')

# Search for any user_ids or emails in details
print("Event types with user / identity links:")
for et in ['LINK_RESOURCE_IDENTITY', 'CLASSIFY_REQUEST', 'RESTORE_BACKUP']:
    subset = df_act[df_act['event_type'] == et]
    print(f"\n--- {et} ({len(subset)}) ---")
    for _, r in subset.head(10).iterrows():
        print(f"[{r['activity_id']}] {r['event_time']} | {r['source_system']} -> {r['target_system']} | res: {r['resource_id']} | res_result: {r['reported_result']} | details: {r['details']}")

# Let's check mentions of 'user_' in details
user_mentions = df_act[df_act['details'].str.contains(r'user_\d+', regex=True, na=False)]
print(f"\nTotal rows mentioning user_\\d+ in details: {len(user_mentions)}")
for _, r in user_mentions.head(10).iterrows():
    print(f"[{r['activity_id']}] {r['details']}")
